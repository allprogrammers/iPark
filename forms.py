from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, SelectField, FileField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo, ValidationError
from models import User

class RegistrationForm(Form):
    fullname = StringField('Full Name: ',validators=[Required(),Length(1,30)],render_kw={"placeholder": "Full Name","class":"form-control"})
    email = StringField('Email: ', validators=[Required(),Length(1,100),Email()],render_kw={"placeholder": "Email address","class":"form-control"})
    phoneno = StringField('Phone No:',render_kw={"placeholder":"Phone Number","class":"form-control"})
    password = PasswordField('Password: ',validators=[Required(),EqualTo('confpassword',message="Passwords do not match")],render_kw={"placeholder": "Password","class":"form-control"})
    confpassword = PasswordField('Confirm Password: ',validators=[Required()],render_kw={"placeholder": "Confirm Password","class":"form-control"})
    submit = SubmitField('Register',render_kw={'class':'btn btn-lg btn-primary btn-block'})

    def validate_email(self,email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already exists')

class BookingForm(Form):
    pass

class LoginForm(Form):
    email = StringField('Email: ', validators=[Required(),Length(1,100),Email()],render_kw={"placeholder": "Email address","class":"form-control"})
    password = PasswordField('Password: ',validators=[Required()],render_kw={"placeholder": "Password","class":"form-control"})
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login',render_kw={'class':'btn btn-lg btn-primary btn-block'})

