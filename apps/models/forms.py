# -*- coding: utf-8 -*-


from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


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
