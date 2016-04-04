# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired

from apps import db


class SearchForm(Form):
    name = StringField('request', validators=[DataRequired()])


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
    school = StringField('request')
    url = StringField('request')



class Post(db.Model):
    __tablename__ = "Post"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(64))
    article = db.Column(db.String(64))
    message = db.Column(db.String(64))
    time = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)


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


