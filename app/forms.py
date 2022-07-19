
from email import message
from email.mime import base
from wtforms import Form, StringField, DateField, PasswordField, IntegerField, DecimalField, validators, HiddenField, SubmitField
from wtforms import Form, StringField, DateField, PasswordField, IntegerField, DecimalField, validators , ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import RecaptchaField

def useremailvalidator(form , field):
    if 'admin.com' in field.data:
        raise ValidationError('Invalid Email Address')


class baseform(Form):
    csrf_token = HiddenField()

class RegistrationForm(baseform):
    email = StringField("Email Address", [validators.Length(min=6, max=35), validators.Email() , useremailvalidator])
    confirmemail = StringField("Confirm Email Address", [validators.Length(min=6, max=35), validators.Email() , validators.EqualTo('email' , message='Email must match')])
    recaptcha = RecaptchaField()


class RegistrationForm2(baseform):
    username = StringField('Username'  , [validators.Length(min=1, max=150), validators.DataRequired()])
    password = PasswordField("Password" , [validators.length(min=8 , message="Please enter a stronger password") , validators.DataRequired() , validators.Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$" , message="Weak Password") ])
    confirmpassword = PasswordField("Confirm Password", [validators.length(min=8) , validators.EqualTo('password' , message='Password must match')])



class LoginForm(baseform):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    password = PasswordField("Password", [validators.DataRequired()])

class TWOFAForm(baseform):
    otp = IntegerField(
        "otp",
        [
            validators.InputRequired(message="Please enter valid otp value."),
            validators.NumberRange(min=000000, max=999999),
        ]
    )

class ProductForm(baseform):
    productimage = FileField(
        "Image",
        validators=[
            FileAllowed(["jpg", "png", "gif", "jpeg"], "Images only please"),
            
        ],
    )
    productname = StringField("Product Name", [validators.Length(min=4, max=25)])
    productdesc = StringField("Product Description", [validators.Length(min=4, max=25)])
    productprice = DecimalField(
        "Price ($)",
        [
            validators.InputRequired(message="Please enter a valid integer value."),
            validators.NumberRange(min=1, max=999999999),
        ], places=2
    )
    productstock = IntegerField(
        "Stock",
        [
            validators.InputRequired(message="Please enter a valid integer value."),
            validators.NumberRange(min=1, max=999999999),
        ]
    )

class RequestResetForm(baseform):
    email = StringField(
        "Email Address", [validators.Length(min=6, max=35), validators.Email()]
    )
class ResetPasswordForm(baseform):
    password = PasswordField(
        "New Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
            validators.length(
                min=8, max=32, message="Password must be at least 8 characters"
            ),
        ],
    )
    confirm = PasswordField("Repeat Password")
