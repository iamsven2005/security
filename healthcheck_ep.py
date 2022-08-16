from cgi import print_arguments
from genericpath import isfile
import smtplib, ssl, shutil, shelve, hashlib, filecmp, os, re, difflib
from dirhash import dirhash
from dotenv import load_dotenv
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_mailman import EmailMessage
from _hashlib import HASH as Hash
from pathlib import Path

basedir = os.getcwd()

load_dotenv()

endpoint_files = ['app/routes/admin/frontpage_ep.py',
                  'app/routes/admin/product_ep.py',
                  'app/routes/admin/user_ep.py',
                  'app/routes/admin/ids_ep.py',
                  'app/routes/admin/admin_ep.py',
                  'app/routes/admin/card_ep.py',
                  'app/routes/auth_ep.py',
                  'app/routes/common_ep.py',
                  'app/routes/order_ep.py',
                  'app/routes/reset_ep.py']

admin_endpoint = ['app/routes/admin/frontpage_ep.py',
                  'app/routes/admin/product_ep.py',
                  'app/routes/admin/user_ep.py',
                  'app/routes/admin/ids_ep.py',
                  'app/routes/admin/admin_ep.py',
                  'app/routes/admin/card_ep.py',]

user_endpoint = ['app/routes/auth_ep.py',
                 'app/routes/common_ep.py',
                 'app/routes/order_ep.py',
                 'app/routes/reset_ep.py']

archive_files = ['archive-frontpage_ep.py',
                 'archive-product_ep.py',
                 'archive-user_ep.py',
                 'archive-ids_ep.py',
                 'archive-admin_ep.py',
                 'archive-card_ep.py',
                 'archive-auth_ep.py',
                 'archive-common_ep.py',
                 'archive-order_ep.py',
                 'archive-reset_ep.py']

admin_file = ['frontpage_ep.py', 'product_ep.py', 'user_ep.py', 'ids_ep.py', 'admin_ep.py', 'card_ep.py']
user_file = ['auth_ep.py', 'common_ep.py', 'order_ep.py', 'reset_ep.py']


def create_healthcheck_table():
    db = shelve.open('healthcheck_data/healthcheck', flag='c')
    healthcheck_dict = {}
    healthcheck_dict['app/routes'] = hash_dir('app/routes', hashlib.md5()).hexdigest()
    for i in endpoint_files:
        healthcheck_dict[i] = hash_file(i, hashlib.md5()).hexdigest()
    db['healthcheck_hash'] = healthcheck_dict
    for i in endpoint_files:
        db[i] = {}
    for i in archive_files:
        db[i] = {}
    print(healthcheck_dict)
    db.close()


def healthcheck():
    now = datetime.now()
    dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
    safe = True
    status = {}

    db = shelve.open('healthcheck_data/healthcheck', flag='c')
    healthcheck_dict = db['healthcheck_hash']
    endpoint_exists = [f for f in endpoint_files if os.path.isfile(f)]
    endpoint_not_exists = [f for f in endpoint_files if not os.path.isfile(f)]
    if endpoint_not_exists != []:
        for i in endpoint_not_exists:
            status[i] = 'Missing'
            safe = False
    for i in endpoint_exists:
        if hash_file(i, hashlib.md5()).hexdigest() != healthcheck_dict[i]:
            status[i] = 'Danger'
            safe = False
    if not safe:
        print('generate report')
        print(status)
        generate_report(dt_string, status)  # generate report and email
        restoredir()
        send_danger_email('', status) #TODO: please add your own email here
    db.close()


def hash_file(file, hash):  # calculate hash value of python file
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash


def hash_dir(directory, hash):  # calculate hash value of route directory
    assert Path(directory).is_dir()
    for path in sorted(Path(directory).iterdir(), key=lambda p: str(p).lower()):
        hash.update(path.name.encode())
        if path.is_file():
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash.update(chunk)
        elif path.is_dir():
            if str(path)[-11:] != '_pycache_':
                hash = hash_dir(path, hash)
    return hash

def generate_report(key, status_dict):
    for i in status_dict:
        if i != 'app/routes':
            if status_dict[i] == 'Danger':
                if i in user_endpoint:
                    create_incidentfile(i.replace('app/routes/', ''), True, False)
                    compare(i.replace('app/routes/', '').replace('.py', '.txt'), key)
                    rmfile(i.replace('app/routes/', ''))
                elif i in admin_endpoint:
                    create_incidentfile(i.replace('app/routes/admin/', ''), True, False)
                    compare(i.replace('app/routes/admin/', '').replace('.py', '.txt'), key)
                    rmfile(i.replace('app/routes/admin/', ''))
            elif status_dict[i] == 'Missing':
                db = shelve.open('healthcheck_data/healthcheck', 'w')
                missing_dict = db[i]
                missing_dict[key] = 'Missing'
                db[i] = missing_dict
                db.close()


def create_backup():
    source = f'{basedir}/app/routes'
    dest = f'{basedir}/backup'
    dest_python = f'{basedir}/backup/pythonfiles'
    dest_txt = f'{basedir}/backup/textfiles'
    dest_txt_admin = f'{basedir}/backup/textfiles/admin'

    # creating python backup
    try:
        shutil.copytree(source, f'{dest}/pythonfiles', ignore=shutil.ignore_patterns('*.pyc'))
        if os.path.exists(f'{dest_python}/_pycache_'):
            shutil.rmtree(f'{dest_python}/_pycache_')
        print('python backup complete')
    except shutil.SameFileError as e:
        print("Backup Failure Error:", e)

    # creating text file backup
    try:
        shutil.copytree(source, f'{dest}/textfiles', ignore=shutil.ignore_patterns('*.pyc'))
        if os.path.exists(f'{dest_txt}/_pycache_'):
            shutil.rmtree(f'{dest_txt}/_pycache_')
        if os.path.exists(f'{dest_txt}/admin/_pycache_'):
            shutil.rmtree(f'{dest_txt}/admin/_pycache_')
        for pyfile in os.listdir(dest_txt):
            if pyfile != 'admin':
                pyfilename = os.path.join(dest_txt, pyfile)
                textfilename = pyfilename.replace('.py', '.txt')
                os.rename(pyfilename, textfilename)
                print(f'{pyfilename}convert file complete')
        for pyfile in os.listdir(dest_txt_admin):
            pyfilename = os.path.join(dest_txt_admin, pyfile)
            textfilename = pyfilename.replace('.py', '.txt')
            os.rename(pyfilename, textfilename)
            print(f'{pyfilename}convert file complete')
    except:
        print("Conversion Error")

def restoredir():
    if os.path.exists('app/routes/'):
        shutil.rmtree('app/routes/')
    shutil.copytree('backup/pythonfiles', 'app/routes/')
    print('files have been restored')

def create_incidentfile(corruptedfile, compare, dt_string):
    if corruptedfile in user_file:
        source = f'{basedir}/app/routes/{corruptedfile}'
    elif corruptedfile in admin_file:
        source = f'{basedir}/app/routes/admin/{corruptedfile}'
    if compare:
        dest = f'{basedir}/incidentfiles/'
        pyfilename = os.path.join(dest, corruptedfile)
    else:
        dest = f'{basedir}/incidentfiles/suspicious/'
        pyfilename = os.path.join(dest, dt_string, corruptedfile)
    shutil.copy2(source, dest)
    textfilename = pyfilename.replace('.py', '.txt')
    os.rename(pyfilename, textfilename)
    print(f'{corruptedfile} has been created')

def compare(filename, dt_string):
    db = shelve.open('healthcheck_data/healthcheck', 'w')
    pyfile = filename.replace('.txt', '.py')
    if pyfile in user_file:
        source = f'app/routes/{pyfile}'
        originalfile = f'{basedir}/backup/textfiles/{filename}'
    elif pyfile in admin_file:
        source = f'app/routes/admin/{pyfile}'
        originalfile = f'{basedir}/backup/textfiles/admin/{filename}'
    route_dict = db[source]

    corruptedfile = f'{basedir}/incidentfiles/{filename}'
    diff_dict = {}

    for line in difflib.unified_diff(open(originalfile).readlines(), open(corruptedfile).readlines(),
                                     fromfile='original file', tofile='corrupted file'):
        if line[0:3] != '---' and line[0:3] != '+++':
            if line[0:2] == '@@':
                num = re.search('-(.*),', line.split()[1]).group(1)
                originalnumline = corruptednumline = int(num)
                key = line.replace('\n', '')
                diff_dict[line.replace('\n', '')] = []
            elif line != '\n':
                if line[0] == '+':
                    diff_dict[key].append(['', corruptednumline, line.replace('\n', '')])
                    corruptednumline += 1
                elif line[0] == '-':
                    diff_dict[key].append([originalnumline, '', line.replace('\n', '')])
                    originalnumline += 1
                else:
                    diff_dict[key].append([originalnumline, corruptednumline, line.replace('\n', '')])
                    corruptednumline += 1
                    originalnumline += 1
    route_dict[dt_string] = diff_dict
    db[source] = route_dict
    print(route_dict)
    db.close()


def rmfile(filename):
    txtfile = filename.replace('.py', '.txt')
    os.remove(f'{basedir}/incidentfiles/{txtfile}')
    print(f'{txtfile} has been deleted')


def send_danger_email(email, corruptedfiles):
    smtp_server = os.getenv('MAIL_SERVER')
    port = os.getenv('MAIL_PORT')  # For starttls port
    sender_email = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    receiver_email = email

    msg = MIMEMultipart()
    msg["Subject"] = "tampered"
    msg["From"] = sender_email
    msg['To'] = email

    text = f'{corruptedfiles.keys()} has been tampered at {datetime.now()}.\n{corruptedfiles}'

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