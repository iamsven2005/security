from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file
from flask_mail import Message
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from uuid import uuid4
import os, pyotp
from datetime import date, datetime, timedelta
from app.forms import RegistrationForm, LoginForm
from app import bcrypt, mysql
from app.utils import *
from functools import wraps

endpoint = Blueprint("auth", __name__)

@endpoint.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    cursor = mysql.connection.cursor()
    if request.method == "POST" and form.validate():
        cursor.execute('SELECT * FROM user WHERE username = %s OR email = %s', (form.username.data, form.email.data,))
        account = cursor.fetchone()
        print(account)
        if account is None:
            hashpwd = bcrypt.generate_password_hash(form.password.data)
            cursor.execute('INSERT INTO user (user_id, username, password, email, role) VALUES (%s, %s, %s, %s, %s)', (str(uuid4())[:8], form.username.data, hashpwd, form.email.data, 'customer'))
            mysql.connection.commit()
            flash('Registration Successfully! Please login before continuing.', category='success')
        else:
            flash('Login credentials already in used.', category='error')
            return redirect(request.referrer)
        return redirect(url_for('base.home'))
    return render_template('auth/register.html', form=form)

@endpoint.route("/login", methods=["GET", "POST"])
def login():
    cursor = mysql.connection.cursor()
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data
        cursor.execute('SELECT * FROM user LEFT JOIN user_otp ON user.user_id = user_otp.user_id WHERE user.username = %s', (username,))
        account = cursor.fetchone()
        print('this is account on line 43', (account))
        user_hashpwd = account['password']
        if account:
            if account['lockout_expiry'] != None:
                lock = datetime.strptime(account['lockout_expiry'], '%Y-%m-%d %H:%M:%S.%f')
                if datetime.now() >= lock:
                    account['lockout_expiry'] = None
                    cursor.execute('UPDATE user SET lockout_expiry = %s WHERE user_id = %s', (None, account['user_id'],))
                    mysql.connection.commit()
                    session['id'] = account['user_id']
                    return redirect(url_for('base.home'))
                else:
                    return redirect(url_for('auth.acc_lockout'))
            elif account and bcrypt.check_password_hash(user_hashpwd, password):
                if account['role'] == 'admin':
                    print(account)
                    session['id'] = account['user_id']
                    return redirect(url_for('admin.frontpage'))
                else:
                    session['id'] = account['user_id']
                    session['username'] = account['username']
                    if account['otp_id'] is None: 
                        session['loggedin'] = True
                        session.permanent = True
                        return redirect(url_for('base.home'))
                    else:
                        return redirect(url_for('auth.login_2fa'))
            elif account and bcrypt.check_password_hash(user_hashpwd, password) is False:
                if account['f_counter']+1 == 5:
                    cursor.execute('UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s', (0, account['f_strike']+1, lockout(account['f_strike']+1),account['user_id'],))
                    mysql.connection.commit()
                    return redirect(url_for('auth.acc_lockout'))
                else:
                    cursor.execute('UPDATE user SET f_counter = %s WHERE user_id = %s', (account['f_counter']+1, account['user_id'],))
                    mysql.connection.commit()
                    flash('Invalid username or password', category='error')
                    return redirect(request.referrer)
        else:
            flash('Invalid username or password', category='error')
            return redirect(request.referrer)
    return render_template('auth/login.html', form=form)

# 2FA page route
@endpoint.route("/login/2fa", methods=['GET', 'POST'])
def login_2fa():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user LEFT JOIN user_otp ON user.user_id = user_otp.user_id WHERE user.user_id = %s', (session['id'],))
    account = cursor.fetchone()
    if account['lockout_expiry'] != None:
        session.pop('id', None)
        return redirect(url_for('auth.acc_lockout'))
    else:
        if request.method == 'POST':
            secret = account['secret']
            # getting OTP provided by user
            otp = int(request.form.get("otp"))

            # verifying submitted OTP with PyOTP
            if pyotp.TOTP(secret).verify(otp):
                # inform users if OTP is valid
                session['loggedin'] = True
                session['username'] = account['username']
                cursor.execute('UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s', (0, 0, None, session['id'],))
                mysql.connection.commit()
                flash("The TOTP 2FA token is valid", "success")
                session.permanent = True
                return redirect(url_for("base.home"))
            else:
                if account['f_counter']+1 == 5:
                    cursor.execute('UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s', (0, account['f_strike']+1, lockout(account['f_strike']+1),account['user_id'],))
                    mysql.connection.commit()
                    return redirect(url_for('auth.acc_lockout'))
                else:
                    cursor.execute('UPDATE user SET f_counter = %s WHERE user_id = %s', (account['f_counter']+1, account['user_id'],))
                    mysql.connection.commit()
                    flash('Invalid username or password', category='error')
                    return redirect(request.referrer)
    return render_template("auth/login_2fa.html")


@endpoint.route('/logout')
@is_loggedin
def logout():
    session.pop('id', None)
    session.pop('username', None)
    session.pop('loggedin', None)
    return redirect(url_for('base.home'))

@endpoint.route('/profile')
def profile():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user LEFT JOIN user_otp ON user.user_id = user_otp.user_id WHERE user.user_id = %s', (session['id'],))
    account = cursor.fetchone()
    return render_template('auth/profile2.html', user=account)

@endpoint.route("/setup-authenticator", methods=['GET'])
def setup():
    secret = pyotp.random_base32()
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user_otp WHERE user_id = %s', (session['id'],))
    account = cursor.fetchone()
    if account is None:
        cursor.execute('INSERT INTO user_otp (user_id, otp_id, secret) VALUES (%s, %s, %s)', (session['id'], 1, secret,)) #when user first set up authenicator
        mysql.connection.commit()
    else:
        cursor.execute('UPDATE user_otp SET secret = %s WHERE user_id = %s AND otp_id = %s', (secret, session['id'], 1,)) #if user reset up their authenticator
        mysql.connection.commit()
    return render_template('auth/authenticator.html', username=session['username'], secret=secret)

@endpoint.route("/account-lockout")
def acc_lockout():
    return render_template("auth/lockout.html")