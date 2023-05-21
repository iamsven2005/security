from flask import Blueprint, render_template, redirect, request, url_for, flash, Flask, Response, session, flash, \
    send_file, abort
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from uuid import uuid4
import os, pyotp, base64, app.forms, random, sys, secrets
from datetime import date, datetime, timedelta
from app.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from app import bcrypt, mysql
from app.utils import *
from functools import wraps

endpoint = Blueprint("reset", __name__)


@endpoint.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = RegistrationForm(request.form)
    if request.method == "GET":
        session['csrf_token'] = base64.b64encode(os.urandom(16))

    if request.method == "POST" and form.validate():
        print(type(form.csrf_token.data))
        print(session.get('csrf_token'))
        if form.csrf_token.data != str(session.get('csrf_token')):
            print('enter')

            flash('CSRF PROTECTION', 'error')

            return redirect(url_for('auth.login'))
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email = %s', (form.email.data,))
        account = cursor.fetchone()
        if account:
            cursor.execute("INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                           (str(uuid4())[:8], account['user_id'], 'low', 'Attempted password reset'))
            mysql.connection.commit()
            send_reset_email(form.email.data)
            cursor.execute('UPDATE user SET token = %s WHERE email = %s',
                           (get_reset_token(form.email.data), form.email.data,))
            mysql.connection.commit()
            flash('An email has been sent with instructions to reset your password', "info")
            print(len(get_reset_token(form.email.data)))
            return redirect(url_for('auth.login'))
        else:
            flash("Could not find the specified email.")
    return render_template("reset/reset_request.html", title='Reset Password', form=form)


@endpoint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    form = ResetPasswordForm(request.form)
    email = s.loads(token, salt='reset-pw', max_age=3600)  # -> this returns u the user's email
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
    account = cursor.fetchone()
    if account:
        if not account['token']:
            flash('Token unavailable', 'error')
            return redirect(url_for('auth.login'))
    if request.method == "GET":
        session['csrf_token'] = base64.b64encode(os.urandom(16))
        try:
            pass
        except SignatureExpired:
            flash('That is an invalid or expired token', 'warning')

    if request.method == "POST" and form.validate():
        print(form.csrf_token.data)
        print(type(form.csrf_token.data))
        print(session.get('csrf_token'))
        if form.csrf_token.data != str(session.get('csrf_token')):
            print('enter')
            flash('CSRF PROTECTION', 'error')
            return redirect(url_for('auth.login'))
        try:
            form = ResetPasswordForm(request.form)
            email = s.loads(token, salt='reset-pw', max_age=3600)  # -> this returns u the user's email
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            account = cursor.fetchone()
            if account:
                if not account['token']:
                    flash('Token unavailable', 'error')
                    return redirect(url_for('auth.login'))
                if request.method == 'POST':
                    hashpwd = bcrypt.generate_password_hash(form.password.data)
                    cursor.execute('UPDATE user SET password = %s, token = %s WHERE email = %s', (hashpwd, None, email,))
                    mysql.connection.commit()
                    flash('Password reset successful', 'info')
                    return redirect(url_for('auth.login'))
            else:
                flash('Invalid Link', "warning")
                return redirect(url_for('auth.login'))
        except SignatureExpired:
            flash('That is an invalid or expired token', 'warning')
            return redirect(url_for('reset_request'))
    return render_template("reset/reset_token.html", title='Reset Password', form=form)