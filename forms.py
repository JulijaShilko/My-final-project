from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, FieldList, FormField, Form, IntegerField, TextAreaField
from wtforms.validators import Email, DataRequired, EqualTo, ValidationError, Length, Regexp, NumberRange
import app
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    email = StringField('Email', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'[A-Z]', message='Password must contain at least one uppercase letter')])
    confirm_password = PasswordField(
        'Repeat password', [DataRequired(), EqualTo('password', 'Passwords must match')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        with app.app.app_context():
            user = app.User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is already in use')

    def validate_name(self, name):
        with app.app.app_context():
            user = app.User.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('This name is already in use')


class LoginForm(FlaskForm):
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class TaskForm(Form):
    task = StringField('Task', validators=[DataRequired()])


class ProgramForm(FlaskForm):
    description = TextAreaField('Discription', validators=[DataRequired()])
    tasks = FieldList(FormField(TaskForm), min_entries=1)
    add_task = SubmitField('Add Task')
    delete_task = SubmitField('Delete Task')
    create = SubmitField('Create')

class PhotoForm(FlaskForm):
    photo = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save')

class CompleteForm(FlaskForm):
    submit = SubmitField('Complete')

    