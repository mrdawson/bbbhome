from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, ValidationError
from flask import request
from app.models import Device


class SearchForm(FlaskForm):
    q = StringField("search", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super().__init__(*args, **kwargs)


class SendBookForm(FlaskForm):
    request_id = HiddenField()
    email = SelectField("Email to", choices=[])
    format = SelectField("Format", choices=[])
    send = SubmitField("Send")

    def set_emails(self, emails):
        self.email.choices = [(e, t) for e, t in emails]

    def set_formats(self, formats):
        self.format.choices = [(f, f) for f in formats]


class NewDeviceForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    submit = SubmitField("Add Device")

    def validate_email(self, email):
        dev = Device.query.filter_by(email=email.data).first()
        if dev is not None:
            raise ValidationError('A device with that email already exists.')