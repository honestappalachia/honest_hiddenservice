#!/usr/bin/env python

# imports and initialization
import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, \
        safe_join, flash, session, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, RadioField, validators, \
        ValidationError, TextAreaField, HiddenField
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('settings.py')
db = SQLAlchemy(app)

# database
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50)) # discriminator
    
    username = db.Column(db.String(80), unique=True)
    pwdhash = db.Column(db.String())
    is_superuser = db.Column(db.Boolean())
    
    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }
    
    def __init__(self, username, password, is_superuser=False):
        self.username = username
        self.pwdhash = generate_password_hash(password)
        self.is_superuser = is_superuser

    def __repr__(self):
        return '<User %r>' % self.username
    
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)
    
class Source(User):
    __tablename__ = 'sources'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'source',
    }

    def __init__(self, username, password):
        super(Source, self).__init__(username, password)
    
    def __repr__(self):
        return '<Source %r>' % self.username
    
class Organization(User):
    __tablename__ = 'organizations'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'organization',
    }

    def __repr__(self):
        return '<Organization %r>' % self.username

class Contact(User):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    email = db.Column(db.String, unique=True)
    public_key = db.Column(db.String)
    
    __mapper_args__ = {
        'polymorphic_identity':'contact',
    }

    def __init__(self, username, password, email, public_key):
        super(Contact, self).__init__(username, password)
        self.email = email
        self.public_key = public_key
    
    def __repr__(self):
        return '<Contact %r>' % self.username
    
def init_db():
    db.create_all()

# forms
class SignupUserChoiceForm(Form):
    user_type_choice = RadioField('What type of user are you?', choices=[
        ('source', 'Source'),
        ('contact', 'Contact')],
        default='source',
        validators=[validators.Required()])

class SignupForm(Form):
    def validate_username(form, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use')
    username = TextField('Username', validators=[validators.Required()])
    password = PasswordField('Password', validators=[
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    recaptcha = RecaptchaField()

class SourceSignupForm(SignupForm):
    user_type = HiddenField(default='source')

class ContactSignupForm(SignupForm):
    user_type = HiddenField(default='contact')
    email = TextField('Email', validators=[validators.Required()])
    public_key = TextAreaField('Public Key', [validators.Required()])

class LoginForm(Form):
    def validate_username(form, field):
        print User.query.filter_by(username=field.data).first()
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError('Invalid username')
    def validate_password(form, field):
        user = User.query.filter_by(username=form.username.data).first()
        if user and not user.check_password(field.data):
            raise ValidationError('Invalid password')
    username = TextField('username', validators=[validators.Required()])
    password = PasswordField('Password', validators=[validators.Required()])

# views

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("You must be logged in to access this page.", 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    def add_and_redirect(user):
        db.session.add(user)
        db.session.commit()
        flash('Successfully signed up', 'success')
        return redirect(url_for('login'))
    user_type = request.values.get('user_type')
    if user_type == 'source':
        form = SourceSignupForm(request.form)
        if form.validate_on_submit():
            return add_and_redirect(Source(form.username.data,
                form.password.data))
    elif user_type == 'contact':
        form = ContactSignupForm(request.form)
        if form.validate_on_submit():
            return add_and_redirect(Contact(form.username.data,
                form.password.data, form.email.data, form.public_key.data))
    else:
        form = SignupUserChoiceForm(request.form)
        if form.validate_on_submit():
            # TODO: make sure form validation covers any malicious input
            return redirect(url_for('signup',
                user_type=form.user_type_choice.data))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        session['logged_in'] = True
        session['user_id'] = user.id
        flash('You were logged in', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'success')
    return redirect(url_for('login'))

@app.route('/settings')
@login_required
def settings():
    user = User.query.get(session.get('user_id'))
    return render_template("settings.html", user=user)

@app.route('/')
@login_required
def index():
    user = User.query.get(session.get('user_id'))
    return render_template("index.html", user=user)

if __name__ == "__main__":
    app.run()
