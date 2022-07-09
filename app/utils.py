from flask import redirect, url_for, session
import os, datetime, smtplib, ssl
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

def is_loggedin(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'loggedin' in session:
			return f(*args,**kwargs)
		else:
			return redirect(url_for('auth.login'), code=307)
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


def send_email(email):
    smtp_server = os.getenv('MAIL_SERVER')
    port = os.getenv('MAIL_PORT')  # For starttls port
    sender_email = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    receiver_email = email
    
    msg = MIMEMultipart()
    msg["Subject"] = "Testing"
    msg["From"] = sender_email
    msg['To'] = receiver_email

    text='test'

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