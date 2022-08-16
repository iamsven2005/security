from datetime import datetime, timedelta
from ipaddress import ip_address
from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, make_response
from app import app, bcrypt, mysql
from app.utils import *
import json
from ast import literal_eval
endpoint = Blueprint("base", __name__)
import datetime
import uuid


@endpoint.route("/")
def home():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product')
    uuids = uuid.uuid4().hex
    products = cursor.fetchall()
    print(session.get('loggedin'))
    return render_template('common/index.html',
                            products_active_keys = products[:4],
                            products_other_keys = products[5:8],
                            uuids=uuids)

@endpoint.route('/product_info/<id>')
def product_info(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product WHERE product_id = %s', (id,))
    product = cursor.fetchone()
    return render_template('common/product_info.html', product=product)

@endpoint.route('/updatefile/')
def updatefile():
    """args req"""
    filename = request.args.get('filename', type=str, default="")
    lines = request.args.get('lines', type=str, default="")
    try:
        if os.path.isfile(filename):
            with open(filename, 'a+') as f:
                if os.stat(filename).st_size > 0:
                    f.write('\n')
                f.write('###'+lines)
    except:
        print('error')
    return redirect(url_for('base.home'))
