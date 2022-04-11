from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import controllers.userControler as userController


def invalid_credentials(form, field):
    email_entered = form.email.data
    password_entered = field.data

    user = userController.checkUser(email_entered)
    user2 = userController.getUser(email_entered, password_entered)

    if user is None:
        raise ValidationError("Incorrect Email or password.")
    elif user2 is None:
        raise ValidationError("Incorrect Email or password")


class SignupForm(FlaskForm):
    user_name = StringField('User name', validators=[
        DataRequired("Please Enter Your First Name"), Length(min=3, max=30, message="UserName should be more than 4 characters")])
    email = StringField('Email', validators=[
                        DataRequired("Please Enter your email address"), Email("Invalid Email!!!")])
    password = PasswordField('Password', validators=[
                             DataRequired("Password Required"), Length(min=6, message="6 or more Characters")])
    confirmPassword = PasswordField('Confirm Password', validators=[
        DataRequired("Password Required"), EqualTo('password', message="Password Must Match")])
    submit = SubmitField('Sign up')

    def validate_user_name(self, user_name):
        user = userController.checkUsername(user_name.data)
        if user:
            raise ValidationError("User Already Exists.")

    def validate_email(self, email):
        user = userController.checkUser(email.data)
        if user:
            raise ValidationError("Email Already Exists.")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(
        "Please Enter your Email"), Email("Invalid Email!!!")])
    password = PasswordField('Password', validators=[
                             DataRequired("Please Enter your Password"), Length(min=6, message="6 or more characters"), invalid_credentials])
    submit = SubmitField('Sign in')


class BooksForm(FlaskForm):
    books = StringField('Book')

    submit = SubmitField('Search')
