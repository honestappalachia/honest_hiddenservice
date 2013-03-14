from datetime import datetime

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50)) # discriminator
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255), unique=True)
    is_superuser = db.Column(db.Boolean())
    
    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }

    def __repr__(self):
        return '<User %r>' % self.username
    
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
