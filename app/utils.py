import requests
from flask import redirect, url_for, session , request , render_template
import os, datetime, smtplib, ssl
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from cryptography.fernet import Fernet
import pickle
from flask_socketio import emit
import math
import socket
from user_agents import parse
s = URLSafeTimedSerializer('secret_key1234')

def is_loggedin(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'loggedin' in session:
			return f(*args,**kwargs)
		else:
			return redirect(url_for('auth.error'), code=307)
	return wrap

def is_admin(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'loggedin' and 'admin' in session:
			return f(*args,**kwargs)
		else:
			return redirect(url_for('auth.error'), code=307)
	return wrap

def lockout(f_strike):
    timeout = {1: 5, 2: 10, 3: 30}
    time_str = str(datetime.now())
    date_format_str = '%Y-%m-%d %H:%M:%S.%f'
    given_time = datetime.strptime(time_str, date_format_str)
    if f_strike < 4:
        final_time = given_time + timedelta(minutes=timeout[f_strike])
    else:
        final_time = given_time + timedelta(minutes=60)
    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    return final_time_str


def send_email(receipient , subject , content):
    smtp_server = os.getenv('MAIL_SERVER')
    port = os.getenv('MAIL_PORT')  # For starttls port
    sender_email = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    receiver_email = receipient
    
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg['To'] = receiver_email


    body_text = MIMEText(content, 'html')  # setting it to plaintext (option available: html, files)
    msg.attach(body_text)  # attaching the text body into msg

    context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # check connection
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # check connection
        server.login(sender_email, password)

        # Send email here
        server.sendmail(sender_email, receiver_email, msg.as_string())

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()



def get_reset_token(email):
    token = s.dumps(email, salt='reset-pw')
    return token

def send_reset_email(email):
    smtp_server = os.getenv('MAIL_SERVER')
    port = os.getenv('MAIL_PORT')  # For starttls port
    sender_email = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    receiver_email = email

    msg = MIMEMultipart()
    msg["Subject"] = 'Forget Password'
    msg["From"] = sender_email
    msg['To'] = receiver_email

    token = get_reset_token(email)
    link = url_for('reset.reset_token', token=token, _external=True)
    text = f'Your link is {link}. This link will expire in 1 hour. If you did not request to reset pw, please ignore this email.'

    body_text = MIMEText(text, 'plain')  # setting it to plaintext (option available: html, files)
    msg.attach(body_text)  # attaching the text body into msg

    context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # check connection
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # check connection
        server.login(sender_email, password)

        # Send email here
        server.sendmail(sender_email, receiver_email, msg.as_string())

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()



def login_by_device(account):
    useremail = account['email']
    usercookie = request.cookies.get('ID')
    useragent = request.headers.get('User-Agent')
    useragentbytes = str.encode(useragent)
    print(usercookie)
    print(account['VirtualDevice_ID'])
    print(useragentbytes)
    try:
        file = open('symmetric.key', 'rb')
        key = file.read()
        file.close()
        f = Fernet(key)
    except FileNotFoundError:
        return
    else:
        encx = f.encrypt(useragentbytes)
        encryptedagent = account['Device_ID'].encode()
        decryptedagent = f.decrypt(encryptedagent)
        print(decryptedagent)
        time = datetime.now()
        formattedtime = time.strftime("%d/%m/%Y %H:%M:%S")
        deviceparsed = parse(useragent)
        if deviceparsed.is_pc:
            deviceused = deviceparsed.os.family + " NT " + deviceparsed.os.version_string

        else:
            deviceused = deviceparsed.os.family + " CPU " + deviceparsed.os.version_string

        if usercookie == account['VirtualDevice_ID'] and useragentbytes == decryptedagent:
            pass

        else:
            me_url = url_for('auth.acceptdevice', email=useremail , usercookie = usercookie , useragent = encx ,_external=True)
            notme_url = url_for('auth.changepasswordnd' , email= useremail , _external=True)
            email_subject = 'New device login activity'
            email_content = render_template('/Email/NewDeviceLogin.html' , time=formattedtime , device =deviceused , email=useremail , me=me_url , notme = notme_url)
            send_email(account['email'] , email_subject , email_content)
    return
