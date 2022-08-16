import re
import json
import time
import MySQLdb.cursors
from flask import current_app
from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file , abort
from flask_mail import Message
from fpdf import FPDF
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
import os, pyotp, base64
from datetime import date, datetime, timedelta
from app.forms import RegistrationForm, LoginForm, TWOFAForm
from app.forms import RegistrationForm, LoginForm , RegistrationForm2 , ChangepasswordForm, CreditForm, AdminForm, TimeForm, QuestionForm
from app import bcrypt, mysql
from app.utils import *
from flask import current_app
from functools import wraps
from app import recaptcha , app , MySQL
from uuid import uuid4
from os.path import exists
import requests

endpoint = Blueprint("auth", __name__)

@endpoint.route("/error", methods=["GET", "POST"])
def error():
    return render_template('error/restriction.html')

@endpoint.route("/register", methods=["GET", "POST"])
def register():
    popup = False
    emaildata = None
    Emailexist = None
    virtualID = request.cookies.get('ID')
    form = RegistrationForm(request.form)
    if request.method == "GET":
        session['csrf_token'] = base64.b64encode(os.urandom(16))

    if request.method == "POST" and form.validate():
        if recaptcha.verify():
            x = request.headers.get('User-Agent')
            useragentbytes = str.encode(x)
            key = Fernet.generate_key()
            file_exists = exists('symmetric.key')
            if file_exists:
                file = open('symmetric.key', 'rb')
                key = file.read()
                file.close()
            else:
                with open("symmetric.key" , "wb") as fo:
                    fo.write(key)

            f = Fernet(key)
            encx = f.encrypt(useragentbytes)
            print(form.csrf_token.data)
            print(type(form.csrf_token.data))
            print(session.get('csrf_token'))
            if form.csrf_token.data != str(session.get('csrf_token')):
                flash('CSRF PROTECTION', 'error')
                return redirect(request.referrer)
            emaildata = form.email.data
            cursor = mysql.connection.cursor()
            cursor.execute('Select email FROM user WHERE email = %(email)s' , {'email' : emaildata})
            checkemail = cursor.fetchone()
            print(checkemail)
            if checkemail ==None:
                print('usernamedoesnotexist')
                cursor.execute("DROP TABLE IF EXISTS TempUser")
                cursor.execute("""CREATE TABLE TempUser ( 
                             user_id varchar(8),
                             username varchar(45),
                             password varchar(255),
                             email varchar(45),
                             status varchar(45),  
                             VirtualDevice_ID varchar(32) NOT NULL,
                             Device_ID varchar(1000) NOT NULL,
                             vstatus varchar(45)
                            ) """)
                cursor.execute('INSERT INTO TempUser Values (%s,%s,%s,%s,%s,%s , %s , %s)' , (None , None , None , emaildata , 'customer' , virtualID , encx , 'pending'))
                mysql.connection.commit()
                token = s.dumps(form.email.data , salt='email-confirm-key')
                token_url = url_for('auth.confirm_email', token=token , emaildata=emaildata , _external=True,)
                email_subject = "Account Email Verification"
                email_html =  render_template('/Email/EmailVerification.html' , token_url = token_url)
                send_email(form.email.data , email_subject , email_html)
                popup = True

            else:
                Emailexist = True
    return render_template('auth/register.html', form=form , _external=True , popup=popup , emaildata = emaildata , Emailexist = Emailexist)


@endpoint.route("/register2/<emaildata>", methods=["GET", "POST"])
def register2(emaildata):
    form = RegistrationForm2(request.form)
    if request.method == "POST" and form.validate():
        hashpwd = bcrypt.generate_password_hash(form.password.data)
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE TempUser SET user_id = %s , username = %s , password = %s WHERE email =%s" , (str(uuid4())[:8] , form.username.data , hashpwd, emaildata))
        cursor.execute("ALTER TABLE TempUser DROP vstatus")
        cursor.execute("INSERT INTO user (user_id , username , password , email , role , VirtualDevice_ID , Device_ID) SELECT * FROM TempUser")
        cursor.execute("DROP TABLE TempUser")
        mysql.connection.commit()
        return redirect(url_for('auth.login'))

    return render_template('auth/CompleteRegister.html' , form=form)


@endpoint.route("/confirm_email/<token>/<emaildata>")
def confirm_email(token , emaildata):
    try:
        cursor = mysql.connection.cursor()
        email = s.loads(token, salt="email-confirm-key", max_age=60)
        cursor.execute('UPDATE TempUser SET vstatus = %s WHERE email = %s' , ('verified' , emaildata))
        mysql.connection.commit()
        print('confirm email ok')
    except SignatureExpired:
        abort(404)

    return render_template('auth/EmailVerified.html')


@endpoint.route('/awaitingsql/<emaildata>')
def awaitingsql(emaildata):
    def generator():
        mysql.connection.commit()
        cursor = mysql.connection.cursor()
        cursor.execute('Select vstatus FROM TempUser WHERE email = %(email)s' , {'email' : emaildata})
        while True:
            status = cursor.fetchone()
            value = status.get('vstatus')
            jsondata = json.dumps({'status' : value})
            print('verified')
            print(value)
            print('generator works')
            time.sleep(1)
            return f"data:{jsondata}\n\n"


    return Response(generator() , mimetype='text/event-stream')


@endpoint.route("/changepasswordnd/<email>" , methods=["GET" , "POST"])
def changepasswordnd(email):
    error = None
    cursor = mysql.connection.cursor()
    cursor.execute('Select * FROM user WHERE email = %(email)s' , {'email' : email})
    account = cursor.fetchone()
    form = ChangepasswordForm(request.form)
    if request.method == "GET":
        session['csrf_token'] = base64.b64encode(os.urandom(16))
    if request.method == "POST" and form.validate():
        if form.csrf_token.data != str(session.get('csrf_token')):
                flash('CSRF PROTECTION', 'error')
                return redirect(request.referrer)
        hashedpwd = bcrypt.generate_password_hash(form.password.data)
        if bcrypt.check_password_hash(account['password'] , form.current_password.data):
            if not bcrypt.check_password_hash(account['password'] , form.password.data):
                cursor.execute("UPDATE user set password = %s where email = %s" , (hashedpwd , email))
                mysql.connection.commit()
            else:
                error = 2
        else:
            error = 1


    return render_template('auth/changepassword.html' , error= error , form=form)

@endpoint.route("/acceptdevice/<email>/<usercookie>/<useragent>")
def acceptdevice(email , usercookie , useragent):
    cursor = mysql.connection.cursor()
    cursor.execute('Select * FROM user WHERE email = %(email)s' , {'email' : email})
    account = cursor.fetchone()
    try:
        file = open('symmetric.key', 'rb')
        key = file.read()
        file.close()
        f = Fernet(key)
    except FileNotFoundError:
        return
    else:
        encryptedagent = account['Device_ID'].encode()
        decryptedagent = f.decrypt(encryptedagent)
        decrypteduser = f.decrypt(useragent.encode())
        if decrypteduser == decryptedagent:
            cursor.execute("UPDATE user SET VirtualDevice_ID = %s WHERE email = %s" ,(usercookie , email))
            mysql.connection.commit()

    return render_template('auth/acceptdevice.html')


@endpoint.route("/login", methods=["GET", "POST"])
def login():
    today = datetime.now()
    date = today.isoweekday()
    cursor = mysql.connection.cursor()
    form = LoginForm(request.form)
    if request.method == "GET":
        session['csrf_token'] = base64.b64encode(os.urandom(16))

    if request.method == "POST" and form.validate():
        print(form.csrf_token.data)
        print(type(form.csrf_token.data))
        print(session.get('csrf_token'))
        if form.csrf_token.data != str(session.get('csrf_token')):
            flash('CSRF PROTECTION', 'error')
            return redirect(request.referrer)

    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data
        cursor.execute(
            'SELECT * FROM user LEFT JOIN user_otp ON user.user_id = user_otp.user_id WHERE user.username = %s',
            (username,))
        account = cursor.fetchone()
        if account:
            user_hashpwd = account['password']
            if account and bcrypt.check_password_hash(user_hashpwd, password):
                if account['lockout_expiry'] != None:
                    lock = datetime.strptime(account['lockout_expiry'], '%Y-%m-%d %H:%M:%S.%f')
                    if datetime.now() >= lock:
                        account['lockout_expiry'] = None
                        cursor.execute('UPDATE user SET lockout_expiry = %s WHERE user_id = %s',
                                       (None, account['user_id'],))
                        mysql.connection.commit()
                        session['id'] = account['user_id']
                        return redirect(url_for('base.home'))
                    else:
                        return render_template('auth/lockout.html')
                if account['Activation'] == 'no':
                    flash("Account does not exist")
                else:
                    if account['status'] == 'admin':
                        session['id'] = account['user_id']
                        session['loggedin'] = True
                        session['admin'] = True
                        cursor.execute(
                                    'UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s',
                                    (0, 0, None, session['id'],))
                        cursor.connection.commit()
                        if account['role'] == 'admin':
                            return redirect(url_for('admin.frontpage'))
                        elif account['role'] == 'card':
                            print("ok")
                            return render_template('admin/cards.html')
                        elif account['role'] == 'user':
                            print("ok")
                            return render_template('admin/user.html')
                    else:
                        if account['Preferred'] == date:
                            session['id'] = account['user_id']
                            session['username'] = account['username']
                            if account['otp_id'] is None:
                                cursor.execute(
                                    "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                                    (str(uuid4())[:8], session['id'], 'good', 'Logged In'))
                                cursor.connection.commit()
                                cursor.execute(
                                    'UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s',
                                    (0, 0, None, session['id'],))
                                cursor.connection.commit()
                                session['loggedin'] = True
                                session.permanent = True
                                login_by_device(account)
                                return redirect(url_for('base.home'))
                            else:
                                return redirect(url_for('auth.login_2fa'))
                        elif account['Preferred'] == None:
                            session['id'] = account['user_id']
                            session['username'] = account['username']
                            if account['otp_id'] is None:
                                cursor.execute(
                                    "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                                    (str(uuid4())[:8], session['id'], 'good', 'Logged In'))
                                cursor.connection.commit()
                                cursor.execute('UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s', (0, 0, None, session['id'],))
                                mysql.connection.commit()
                                session['loggedin'] = True
                                session.permanent = True
                                login_by_device(account)
                                return redirect(url_for('base.home'))
                            else:
                                return redirect(url_for('auth.login_2fa'))
                        else:
                            session['id'] = account['user_id']
                            session['username'] = account['username']
                            return redirect(url_for('auth.login_security'))
            elif account and bcrypt.check_password_hash(user_hashpwd, password) is False:
                # Insert record failed login of user
                cursor.execute(
                    "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                    (str(uuid4())[:8], account['user_id'], 'high', 'Failed login'))
                mysql.connection.commit()
                if account['f_counter'] + 1 == 5:
                    cursor.execute(
                        'UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s',
                        (0, account['f_strike'] + 1, lockout(account['f_strike'] + 1), account['user_id'],))
                    mysql.connection.commit()
                    return render_template("auth/lockout.html")
                else:
                    cursor.execute('UPDATE user SET f_counter = %s WHERE user_id = %s',
                                   (account['f_counter'] + 1, account['user_id'],))
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
    form = TWOFAForm(request.form)
    if request.method == "GET":
        session['csrf_token'] = base64.b64encode(os.urandom(16))

    if request.method == "POST" and form.validate():
        print(form.csrf_token.data)
        print(type(form.csrf_token.data))
        print(session.get('csrf_token'))
        if form.csrf_token.data != str(session.get('csrf_token')):
            flash('CSRF PROTECTION', 'error')
            return redirect(request.referrer)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user LEFT JOIN user_otp ON user.user_id = user_otp.user_id WHERE user.user_id = %s',
                   (session['id'],))
    account = cursor.fetchone()
    if account['lockout_expiry'] != None:
        session.pop('id', None)
        return render_template("auth/lockout.html")
    else:
        if request.method == "POST" and form.validate():
            print(form.csrf_token.data)
            print(type(form.csrf_token.data))
            print(session.get('csrf_token'))
            if form.csrf_token.data != str(session.get('csrf_token')):
                flash('CSRF PROTECTION', 'error')
                return redirect(request.referrer)
        if request.method == 'POST' and form.validate():
            print(account)
            secret = account['secret']
            # getting OTP provided by user
            otp = int(form.otp.data)

            # verifying submitted OTP with PyOTP
            if pyotp.TOTP(secret).verify(otp):
                # inform users if OTP is valid
                session['loggedin'] = True
                session['username'] = account['username']
                cursor.execute('UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s',
                               (0, 0, None, session['id'],))
                mysql.connection.commit()
                flash("The TOTP 2FA token is valid", "success")
                session.permanent = True
                return redirect(url_for("base.home"))
            else:
                # Insert record of failed 2FA of user
                cursor.execute(
                    "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                    (str(uuid4())[:8], account['user_id'], 'high', 'Failed 2FA'))
                mysql.connection.commit()
                if account['f_counter'] + 1 == 5:
                    cursor.execute(
                        'UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s',
                        (0, account['f_strike'] + 1, lockout(account['f_strike'] + 1), account['user_id'],))
                    mysql.connection.commit()
                    return render_template("auth/lockout.html")
                else:
                    cursor.execute('UPDATE user SET f_counter = %s WHERE user_id = %s',
                                   (account['f_counter'] + 1, account['user_id'],))
                    mysql.connection.commit()
                    flash('Invalid username or password', category='error')
                    return redirect(request.referrer)
    return render_template("auth/login_2fa.html", form=form)

@endpoint.route('/fakelogin')
def fakelogin():
    form = LoginForm(request.form)
    return render_template('auth/fakelogin.html', form=form)

@endpoint.route('/logout')
@is_loggedin
def logout():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
        (str(uuid4())[:8], session['id'], 'good', 'Logged out'))
    cursor.connection.commit()
    session.pop('id', None)
    session.pop('username', None)
    session.pop('loggedin', None)
    session.pop('admin', None)

    return redirect(url_for('base.home'))


@endpoint.route('/profile')
@is_loggedin
def profile():
    print(session.get('new_device'))
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user LEFT JOIN user_otp ON user.user_id = user_otp.user_id WHERE user.user_id = %s', (session['id'],))
    account = cursor.fetchone()
    return render_template('auth/profile.html', user=account)

@endpoint.route("/setup-authenticator", methods=['GET', 'POST'])
@is_loggedin
def setup():
    form = TWOFAForm(request.form)
    if request.method == "GET":
        session['csrf_token'] = base64.b64encode(os.urandom(16))

    if request.method == "POST" and form.validate():
        print(form.csrf_token.data)
        print(type(form.csrf_token.data))
        print(session.get('csrf_token'))
        if form.csrf_token.data != str(session.get('csrf_token')):
            flash('CSRF PROTECTION', 'error')
            return redirect(request.referrer)
    if request.method == 'GET':
        secret = pyotp.random_base32()
    if request.method == 'POST':
        secret = request.form.get("secret")
        otp = int(request.form.get("otp"))
        if pyotp.TOTP(secret).verify(otp):
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user_otp WHERE user_id = %s', (session['id'],))
            account = cursor.fetchone()
            if account is None:
                cursor.execute('INSERT INTO user_otp (user_id, otp_id, secret) VALUES (%s, %s, %s)', (session['id'], 1, secret,)) #when user first set up authenicator
                cursor.execute(
                    "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                    (str(uuid4())[:8], session['id'], 'good', 'Authenticator Added'))
            else:
                cursor.execute('UPDATE user_otp SET secret = %s WHERE user_id = %s AND otp_id = %s', (secret, session['id'], 1,)) #if user reset up their authenticator
                cursor.execute(
                    "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                    (str(uuid4())[:8], session['id'], 'good', 'Authenticator Updated'))
            mysql.connection.commit()
            flash('2FA has been enabled!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid OTP', 'danger')
            return redirect(request.referrer)
    return render_template('auth/authenticator.html', username=session['username'], secret=secret, form=form)

@endpoint.route("/disable-2fa",methods=['GET','POST'])
@is_loggedin
def disable():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM user_otp WHERE user_id = %s AND otp_id = %s', (session['id'], 1,))
        cursor.execute(
            "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
            (str(uuid4())[:8], session['id'], 'good', 'Authenticator has been disabled'))
        mysql.connection.commit()
        return redirect(request.referrer)

@endpoint.route("/account-lockout")
def acc_lockout():
    return render_template("auth/lockout.html")

@endpoint.route("/addcard", methods=["GET", "POST"])
@is_loggedin
def addcard():
    form = CreditForm(request.form)
    card_id = str(uuid4())[:5]
    if request.method == 'POST' and form.validate():
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT cc_id FROM credit_card WHERE cc_id = %s', [id])
        credit = cursor.fetchone()
        if credit is None:
            try:
                hashcc = bcrypt.generate_password_hash(form.card_number.data)
                cursor.execute(
                    'INSERT INTO credit_card(cc_id, cvv, exp_mm,exp_yy, cc_username,user_id, card_id,en_cc_id) '
                    'VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (form.card_number.data, form.cvv.data,
                                                         form.exp_mm.data, form.exp_yy.data, form.creditName.data,
                                                         session['id'], card_id, hashcc))
                print((hashcc))
                mysql.connection.commit()
                cursor.execute(
                    "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                    (str(uuid4())[:8],session['id'] , 'good', 'Added Credit Card'))

                mysql.connection.commit()
                flash("Card has been added")
            except:
                flash("This card has already been used cannot be added")
                print("cannot")

        return redirect(url_for('auth.credit_card'))
    return render_template('/auth/credit_form.html', form=form)


@endpoint.route("/payment", methods=["GET", "POST"])
@is_loggedin
def credit_card():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * From credit_card')
    creditt = cursor.fetchall()
    return render_template('auth/credit.html', creditt=creditt)


@endpoint.route('/deletecc/<id>', methods=['POST'])
@is_loggedin
def deletecc(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM credit_card WHERE card_id = %s', [id])
    cursor.execute(
        "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
        (str(uuid4())[:8], session['id'], 'good', 'Removed Credit Card'))
    cursor.connection.commit()
    return redirect(request.referrer)

@endpoint.route("/history", methods=["GET", "POST"])
@is_loggedin
def history():
    # gets the date 30 days ago from current time to query failed logins
    datenow = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    cursor.execute("""SELECT activity.user_id, severity, timestamp, description FROM secprj.activity 
        LEFT JOIN secprj.user 
        ON activity.user_id = user.user_id
        WHERE user.status = 'customer'
        AND activity.timestamp >= %s
        ORDER BY timestamp DESC;""", (datenow,))
    activity = cursor.fetchall()
    return render_template('auth/history.html', activity = activity, users = users)


@endpoint.route("/download/report/pdf", methods=["GET", "POST"])
@is_loggedin
def download_report():

    datenow = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cursor = mysql.connection.cursor()

    cursor.execute("""SELECT activity.user_id, severity, timestamp, description, username FROM secprj.activity 
            LEFT JOIN secprj.user 
            ON activity.user_id = user.user_id
            WHERE activity.user_id = %s
            AND activity.timestamp >= %s
            AND activity.severity = 'good'
            ORDER BY timestamp DESC;""", (session['id'], datenow))
    result = cursor.fetchall()

    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w - 2 * pdf.l_margin

    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(page_width, 0.0, 'History Records', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 9)

    col_width = page_width / 3

    pdf.ln(5)



    for row in result:
        pdf.cell(col_width, 10, str(row['username']), border=1)
        pdf.cell(col_width, 10, str(row['timestamp']), border=1)
        pdf.cell(col_width, 10, row['description'], border=1)
        pdf.ln(10)

    pdf.ln(10)

    pdf.set_font('Times', '', 10.0)
    pdf.cell(page_width, 0.0, '- end of report -', align='C')

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=History Records.pdf'})

@endpoint.route("/preferred/<id>", methods=["GET", "POST"])
@is_loggedin
def preferred(id):
    form = TimeForm(request.form)
    cursor = mysql.connection.cursor()
    if request.method == 'POST' and form.validate():
        cursor.execute('SELECT * FROM user WHERE user_id=%s', [id])
        users = cursor.fetchone()
        if users:
            try:
                cursor.execute('UPDATE user SET  Question = %s, Preferred = %s WHERE user_id = %s', [form.question.data,form.time.data,[id]])
                mysql.connection.commit()
                flash("Time Preferred has been set")
                cursor.execute(
                    "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                    (str(uuid4())[:8], session['id'], 'good', 'Preferred Time added'))
                cursor.connection.commit()
            except:
                flash("Got Error")
                print("cannot")
        else:
            flash("Got Error")
            print("cannot")

        return redirect(url_for('auth.profile'))
    return render_template('auth/securityqns.html', form= form)

@endpoint.route("/noPreferred/<id>", methods=["GET", "POST"])
@is_loggedin
def noPreferred(id):
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE user SET  Preferred = %s, Question = %s WHERE user_id = %s', [None,None,id])
    cursor.connection.commit()
    cursor.execute(
        "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
        (str(uuid4())[:8], session['id'], 'good', 'Preferred Time Removed'))
    cursor.connection.commit()
    return redirect(request.referrer)

@endpoint.route("/login/security", methods=['GET', 'POST'])
def login_security():
    form = QuestionForm(request.form)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user WHERE user_id=%s',([session['id']]) )
    account = cursor.fetchone()
    if request.method == 'POST' and form.validate():
        # getting OTP provided by user
        quest = (form.question.data)
        question = quest.lower()
        if question.lower() == account["Question"].lower():
            print("ok")
            # inform users if OTP is valid
            session['loggedin'] = True
            session['username'] = account['username']
            cursor.execute(
                "INSERT INTO activity (activityid, user_id, severity, description) VALUES (%s, %s, %s, %s)",
                (str(uuid4())[:8], session['id'], 'good', 'Logged In'))
            cursor.connection.commit()
            cursor.execute('UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s', (0, 0, None, session['id'],))
            mysql.connection.commit()
            flash("The Security Question is correct!", "success")
            session.permanent = True
            return redirect(url_for("base.home"))
        else:
            # Insert record of failed 2FA of user
            if account['f_counter'] + 1 == 5:
                cursor.execute(
                    'UPDATE user SET f_counter = %s, f_strike = %s, lockout_expiry = %s WHERE user_id = %s',
                    (0, account['f_strike'] + 1, lockout(account['f_strike'] + 1), account['user_id'],))
                mysql.connection.commit()
                return render_template("auth/lockout.html")
            else:
                cursor.execute('UPDATE user SET f_counter = %s WHERE user_id = %s',
                               (account['f_counter'] + 1, account['user_id'],))
                mysql.connection.commit()
                flash("Security Question is wrong please try again!")
                return redirect(request.referrer)
    return render_template("auth/login_security.html", form=form)