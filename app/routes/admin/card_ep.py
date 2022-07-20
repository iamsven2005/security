from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file
from app import app, bcrypt, mysql
from app.forms import *
from PIL import Image
from uuid import uuid4
import os
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from passlib.hash import sha256_crypt
basedir = os.getcwd()
# hashcc = sha256_crypt.encrypt("SELECT cc_id FROM credit_card")

endpoint = Blueprint("credit", __name__)

@endpoint.route('/credit')
def credit():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM credit_card')
    credits = cursor.fetchall()
    return render_template('admin/credit/credit.html', credits = credits)

@endpoint.route('/cardManager')
def cardManager():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM credit_card')
    credits = cursor.fetchall()
    return render_template('admin/cardManager/card_manager.html', credits = credits)