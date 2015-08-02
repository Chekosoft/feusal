# encoding: utf-8
from flask_wtf import Form

from wtforms import StringField, FieldList, DateTimeField, SelectField, RadioField, FormField
from wtforms import validators

class CampusForm(Form):
    campuses = FieldList(StringField(validators=[validators.InputRequired()]), validators=[validators.Length(min=1)])

class ElectionOption(Form):
    name = StringField(validators=[validators.InputRequired()])
    detail = StringField()

class NewElectionForm(Form):
    reason = StringField(validators=[validators.InputRequired()])
    selectedCampus = StringField(validators=[validators.InputRequired()])
    date_from = DateTimeField(validators=[validators.InputRequired()])
    date_until = DateTimeField(validators=[validators.InputRequired()])
    electionOptions = FieldList(FormField(ElectionOption), validators=[validators.Length(min=2)])