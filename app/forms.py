from email import message
from email.mime import base
from wtforms import Form, StringField, DateField, PasswordField, IntegerField, DecimalField, validators, HiddenField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired


class baseform(Form):
    csrf_token = HiddenField()

class RegistrationForm(baseform):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    email = StringField(
        "Email Address", [validators.Length(min=6, max=35), validators.Email()]
    )
    dob = DateField("Date Of Birth", format="%Y-%m-%d")
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