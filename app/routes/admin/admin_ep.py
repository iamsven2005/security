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

endpoint = Blueprint("table", __name__)

@endpoint.route('/table')
def table():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user')
    table = cursor.fetchall()
    return render_template('admin/table/admins.html', admins = table)

@endpoint.route('/addAdmin', methods=["GET", "POST"])
def addAdmin():
    form = AdminForm(request.form)
    cursor = mysql.connection.cursor()
    if request.method == "POST" and form.validate():
        cursor.execute('SELECT * FROM user WHERE email = %s', (form.email.data,))
        admin = cursor.fetchone()
        if admin is None:
            hashpwd = bcrypt.generate_password_hash(form.password.data)
            cursor.execute(
                'INSERT INTO user (user_id, username, password, email,status, role) VALUES (%s, %s, %s, %s, %s, %s)',
                (str(uuid4())[:8], form.username.data, hashpwd, form.email.data,form.status.data, form.role.data))
            mysql.connection.commit()
            flash('Account has been added', category='success')
        else:
            flash("There is already a same email in the database.", category='error')


        return redirect(url_for('table.table'))
    return render_template('admin/table/add_admin.html', form = form)

@endpoint.route('/updateAdmin/<id>', methods=['GET', 'POST'])
def updateAdmin(id):
    form = AdminForm(request.form)
    cursor = mysql.connection.cursor()
    if request.method == 'POST' and form.validate():
        cursor.execute('SELECT * FROM user WHERE user_id = %s', [id])
        updateAdmin = cursor.fetchone()
        if updateAdmin:
            hashpwd = bcrypt.generate_password_hash(form.password.data)
            cursor.execute('UPDATE user SET  username = %s, password = %s, email = %s,status = %s, role = %s WHERE user_id = %s' ,
                            [form.username.data, hashpwd,form.email.data, form.status.data, form.role.data, id])
            mysql.connection.commit()
            flash('Account has been added', category='success')
        else:
            flash("There is already a same email in the database.", category='error')
        return redirect(url_for('table.table'))
    return render_template('admin/table/add_admin.html', form=form)