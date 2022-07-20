
from email import message
from email.mime import base
from wtforms import Form, StringField, DateField, PasswordField, IntegerField, DecimalField, validators, HiddenField, SubmitField, SelectField
from wtforms import Form, StringField, DateField, PasswordField, IntegerField, DecimalField, validators , ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import RecaptchaField
def validate_card(form, field):
    card_number = field.data
    temp = str(card_number)

    sum_1 = 0
    sum_2 = 0

    index = len(temp) - 1

    while index >= 0:
        sum_1 += int(temp[index])
        index -= 2

    index = len(temp) - 2
    while index >= 0:
        number = int(temp[index]) * 2
        if number >= 10:
            number = str(number)
            sum_2 += int(number[0]) + int(number[1])
        else:
            sum_2 += number
        index -= 2

    sum_of_total = str(sum_2 + sum_1)
    validation = int(sum_of_total[len(sum_of_total) - 1])

    if validation != 0:
        raise ValidationError('Card number is Invalid')

def validatecvv(form, field):
    if len(field.data) > 4 or len(field.data) < 3:
        raise ValidationError('Enter the 3 or 4 digit number that is found at the back of the credit/debit card')

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
class CreditForm(baseform):
    card_number = StringField('Card Number', [validators.length(min=13, max=16), validators.data_required(),validate_card])
    cvv = PasswordField('CVV',  [validators.data_required(),validatecvv])

    exp_mm = SelectField('Expiration MM',
                         choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                                  ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')], coerce=str)
    exp_yy = SelectField('Expiration YY',
                         choices=[('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'),
                                  ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
                                  ('2030', '2030'), ('2031', '2031'), ('2032', '2032')], coerce=str)
    creditName = StringField("credit Name", [validators.Length(min=4, max=100)])

class AdminForm(baseform):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    email = StringField(
        "Email Address", [validators.Length(min=6, max=35), validators.Email()]
    )
    password = PasswordField(
        "New Password",
        [
            validators.DataRequired(),
            validators.length(
                min=8, max=32, message="Password must be at least 8 characters"
            ),
            validators.Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",message="Weak Password")
        ],
    )
    status = SelectField('Status', [validators.Length(min=1, max=50), validators.DataRequired()],
                       choices=[('', 'Select'), ('admin', 'admin'), ('customer', 'customer')], default='')
    role = SelectField('Role', [validators.Length(min=1, max=50), validators.DataRequired()],
                           choices=[('', 'Select'), ('admin', 'admin'),('card', 'card'),('user', 'user')], default='')