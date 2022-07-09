from datetime import datetime, timedelta
from ipaddress import ip_address
from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, make_response
from app import app, bcrypt, mysql
from app.utils import *
import json
from ast import literal_eval

endpoint = Blueprint("base", __name__)

@endpoint.route("/")
def home():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product')
    products = cursor.fetchall()
    return render_template('common/index.html',
                            products_active_keys = products[:4],
                            products_other_keys = products[5:8])

@endpoint.route('/product_info/<id>')
def product_info(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product WHERE product_id = %s', (id,))
    product = cursor.fetchone()
    return render_template('common/product_info.html', product=product)