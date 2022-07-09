from wtforms import Form, StringField, DateField, PasswordField, IntegerField, DecimalField, validators
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(Form):
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

class LoginForm(Form):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    password = PasswordField("Password", [validators.DataRequired()])

class ProductForm(Form):
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
