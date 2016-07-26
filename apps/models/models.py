# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired

from apps import db


###############################################################################
# Define forms to interact with application:
###############################################################################
class SearchForm(Form):
    name = StringField('request', validators=[DataRequired()])

class ExtendedSearchForm(Form):
    name = StringField('request', validators=[DataRequired()])
    source = StringField('request', validators=[DataRequired()])

class LoginForm(Form):
    name = StringField('request', validators=[DataRequired()])
    passwd = StringField('request', validators=[DataRequired()])


class BiblioForm(Form):
    author = StringField('request', validators=[DataRequired()])
    title = StringField('request', validators=[DataRequired()])
    year = IntegerField('request', validators=[DataRequired()])
    typ = StringField('request', validators=[DataRequired()])
    journal = StringField('request')
    ID = StringField('request', validators=[DataRequired()])
    keywords = StringField('request')
    tag = StringField('request')
    school = StringField('request')
    url = StringField('request')


class PostForm(Form):
    message = TextAreaField('request')


###############################################################################
# Define ORM for app database:
###############################################################################
class Post(db.Model):
    __tablename__ = "Post"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(64))
    article = db.Column(db.String(64))
    message = db.Column(db.String(2048))
    time = db.Column(db.Integer)


class Event(db.Model):
    __tablename__ = "Event"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(64))
    article = db.Column(db.String(64))
    event = db.Column(db.String(16))
    time = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    passwd = db.Column(db.String(120), index=True, unique=True)
    authenticated = db.Column(db.Boolean, default=False)

    def get_id(self):
        return self.id
    def is_active(self):
        return True
    def is_authenticated(self):
        return self.authenticated
    def is_anonymous(self):
        return False


class BiblioEntry(db.Model):
    __tablename__ = "Biblio"
    ID = db.Column(db.String, primary_key=True)
    ENTRYTYPE = db.Column(db.String)
    authors = db.Column(db.String)
    title = db.Column(db.String)
    year = db.Column(db.Integer)
    month = db.Column(db.String)
    publisher = db.Column(db.String)
    journal = db.Column(db.String)
    school = db.Column(db.String)
    pdf = db.Column(db.String)
    url = db.Column(db.String)
    keywords = db.Column(db.String)
    tag = db.Column(db.String)

