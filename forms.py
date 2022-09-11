from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, DateField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from datetime import date


class RecordForm(FlaskForm):
	name = StringField("Name: ", validators=[DataRequired(message="You need to enter the name")])
	birthday = DateField('Birthday', format='%Y-%m-%d', validators=[DataRequired(message="You need to enter the birthday")])
	email = StringField("Email", validators=[Email(), DataRequired(message="You need to enter the email")],)
	phone = StringField("Phone", validators=[DataRequired(message="You need to enter the phone"), Length(min = 10, max = 13)],)
	phone2 = StringField("Phone", validators=[DataRequired(message="You need to enter the phone"), Length(min = 10, max = 13)],)
	address = StringField("Address", validators=[DataRequired(message="You need to enter the address")],)
	submit = SubmitField("Submit")


# class LoginForm(FlaskForm):
#     email = StringField("Email: ", validators=[Email("Некорректный email")])
#     psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
#     remember = BooleanField("Запомнить", default = False)
#     submit = SubmitField("Войти")

# class RegisterForm(FlaskForm):
#     name = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
#     email = StringField("Email: ", validators=[Email("Некорректный email")])
#     psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
#     psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
#     submit = SubmitField("Регистрация")