from email import message
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, \
    IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo,\
    ValidationError
from models import User, db_session


class RegistrationForm(FlaskForm):
    username = StringField("Username",
                           validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email",
                        validators=[DataRequired(), Email(), Length(min=2, max=150)])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords don't match")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = db_session.query(User).filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is taken! Choose another")

    def validate_email(self, email):
        email = db_session.query(User).filter_by(email=email.data).first()
        if email:
            raise ValidationError("That email is taken! Choose another")


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")




class RecordForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired(message="You need to enter the name")])
    birthday = DateField('Birthday', format='%Y-%m-%d', validators=[DataRequired(message="You need to enter the birthday")])
    phone = StringField("Phone", validators=[DataRequired(message="You need to enter the phone"), Length(min = 10, max = 13)],)
    email = StringField("Email", validators=[Email(), DataRequired(message="You need to enter the email")],)
    address = StringField("Address", validators=[DataRequired(message="You need to enter the address")],)
    submit = SubmitField("Submit")
