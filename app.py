#!/usr/bin/env python

# imports and initialization
import os

from flask import Flask, render_template, request, redirect, url_for, \
        safe_join, flash, session, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators, ValidationError
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')
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
    
    __mapper_args__ = {
        'polymorphic_identity':'contact',
    }
    
    def __repr__(self):
        return '<Contact %r>' % self.username
    
def init_db():
    db.create_all()

# forms
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.password.data)
        # TODO handle exceptions from database
        db.session.add(user)
        db.session.commit()
        flash('Successfully signed up')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        session['logged_in'] = True
        session['user_id'] = user.id
        flash('You were logged in')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/users/<username>')
def user_profile(username):
    if not session.get('logged_in'):
        abort(401)
    if User.query.get(session.get('user_id')).username != username:
        abort(403)
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user=user)

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user = User.query.get(session.get('user_id'))
    return render_template("index.html", user=user)

if __name__ == "__main__":
    app.run()
