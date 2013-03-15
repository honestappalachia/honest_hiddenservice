#!/usr/bin/env python

# imports and initialization
import os

from flask import Flask, render_template, request, redirect, url_for, \
        safe_join, flash, session, abort
from flask.ext.sqlalchemy import SQLAlchemy
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

# views

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if not user:
            error = "Invalid username"
        elif not user.check_password(request.form['password']):
            error = "Invalid password"
        else:
            session['logged_in'] = True
            session['user_id'] = user.id
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        if request.form['username'] == '':
            error = "You must specify a username."
        elif request.form['password'] == '':
            error = "You must specify a password."
        elif User.query.filter_by(username=request.form['username']).first() \
                != None:
            error = "That username is already in use."
        else:
            try:
                new_user = User(request.form['username'],
                                request.form['password'])
                db.session.add(new_user)
                db.session.commit()
                # Log the newly added user in
                session['logged_in'] = True
                session['user_id'] = new_user.id
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                error = "An unspecified error occurred. Please report this."
    return render_template('signup.html', error=error)

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
