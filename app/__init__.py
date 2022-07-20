from flask import Flask, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mysqldb import MySQL
from datetime import timedelta
import os
from dotenv import load_dotenv
from flask_recaptcha import ReCaptcha
from markupsafe import Markup
# from healthcheck_ep import hash_ep

load_dotenv()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('secret_key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 #setting 16 * 1000 * 1000 returns 16mb megabyte
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']

bcrypt = Bcrypt(app)

#flask-mysqldb config
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS')
mysql = MySQL(app)

#flask-limiter config
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "5 per seconds"]
)


#RECAPTCHA

app.config['RECAPTCHA_ENABLED'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LfCX_EgAAAAAJUgvFM1q0CUCd7rpczzYHsoE6vJ"
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfCX_EgAAAAAJB_BLVtbqU3HtTwBbfr-7L72c_N'


recaptcha = ReCaptcha()
recaptcha.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html')

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error/429.html')



from app.routes.common_ep import endpoint as EP_Common
from app.routes.auth_ep import endpoint as EP_Auth
from app.routes.order_ep import endpoint as EP_Order
from app.routes.reset_ep import endpoint as EP_Reset
from app.routes.admin.frontpage_ep import endpoint as EP_Admin_Frontpage
from app.routes.admin.product_ep import endpoint as EP_Admin_Product
from app.routes.admin.user_ep import endpoint as EP_Admin_User
from app.routes.admin.card_ep import endpoint as EP_Admin_Card
from app.routes.admin.admin_ep import endpoint as EP_Admin_Admin

app.register_blueprint(EP_Common, url_prefix="/")
app.register_blueprint(EP_Auth, url_prefix="/")
app.register_blueprint(EP_Order, url_prefix="/")
app.register_blueprint(EP_Reset, url_prefix="/")
app.register_blueprint(EP_Admin_Frontpage, url_prefix="/admin")
app.register_blueprint(EP_Admin_Product, url_prefix="/admin")
app.register_blueprint(EP_Admin_User, url_prefix="/admin")
app.register_blueprint(EP_Admin_Card, url_prefix="/admin")
app.register_blueprint(EP_Admin_Admin, url_prefix="/admin")

