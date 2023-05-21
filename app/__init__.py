from flask import Flask, render_template, request, redirect, url_for, abort
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mysqldb import MySQL
from datetime import timedelta
from dotenv import load_dotenv
from flask_recaptcha import ReCaptcha
from flask_session import Session
from markupsafe import Markup
from healthcheck_ep import *
import os, geocoder

load_dotenv()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('secret_key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 #setting 16 * 1000 * 1000 returns 16mb megabyte
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
bcrypt = Bcrypt(app)

#flask-mysqldb config
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '5002nevsmai!'
app.config['MYSQL_DB'] = 'secprj'

mysql = MySQL(app)


#flask-limiter config
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])


#RECAPTCHA

app.config['RECAPTCHA_ENABLED'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'


recaptcha = ReCaptcha()
recaptcha.init_app(app)

@app.before_first_request
def before_first_request():
    basedir = os.getcwd()
    if not os.path.isdir(f'{basedir}/backup/pythonfiles'):
        create_backup()
    if not os.path.isfile(f'healthcheck_data/healthcheck.dat'):
        create_healthcheck_table()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html')

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error/429.html')

@app.errorhandler(403)
def perms_error(e):
  return render_template('error/403.html')


from app.routes.common_ep import endpoint as EP_Common
from app.routes.auth_ep import endpoint as EP_Auth
from app.routes.order_ep import endpoint as EP_Order
from app.routes.reset_ep import endpoint as EP_Reset
from app.routes.admin.frontpage_ep import endpoint as EP_Admin_Frontpage
from app.routes.admin.product_ep import endpoint as EP_Admin_Product
from app.routes.admin.user_ep import endpoint as EP_Admin_User
from app.routes.admin.card_ep import endpoint as EP_Admin_Card
from app.routes.admin.admin_ep import endpoint as EP_Admin_Admin
from app.routes.admin.ids_ep import endpoint as EP_Admin_Ids
app.register_blueprint(EP_Common, url_prefix="/")
app.register_blueprint(EP_Auth, url_prefix="/")
app.register_blueprint(EP_Order, url_prefix="/")
app.register_blueprint(EP_Reset, url_prefix="/")
app.register_blueprint(EP_Admin_Frontpage, url_prefix="/admin")
app.register_blueprint(EP_Admin_Product, url_prefix="/admin")
app.register_blueprint(EP_Admin_User, url_prefix="/admin")
app.register_blueprint(EP_Admin_Card, url_prefix="/admin")
app.register_blueprint(EP_Admin_Admin, url_prefix="/admin")
app.register_blueprint(EP_Admin_Ids, url_prefix="/admin")
