from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Email, DataRequired, Length, EqualTo


class LoginForm(FlaskForm):

    email = StringField('Email: ', validators=[Email()])
    psw = PasswordField("Password: ", validators=[DataRequired(), Length(min=4, max=100)])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):

    name = StringField("Имя: ", validators=[Length(min=5, max=100)])
    email = StringField("Email: ", validators=[Email()])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100)])
    psw2 = PasswordField("Повторите пароль: ", validators=[EqualTo("psw")])
    submit = SubmitField("Регистрация")
