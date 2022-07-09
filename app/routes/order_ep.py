from datetime import datetime, timedelta
from ipaddress import ip_address
from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, make_response
from app import app, bcrypt, mysql
from app.utils import *
import json
from ast import literal_eval

endpoint = Blueprint("order", __name__)

@endpoint.route('/cart')
@is_loggedin
def cart():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user WHERE user_id = %s', (session['id'],))
    account = cursor.fetchone()
    cart = literal_eval(account['cart']) #gives us quantity of what they ordered (dict)
    product: list = [] #gives us product details from product table (list)
    for i in cart:
        cursor.execute('SELECT * FROM product WHERE product_id = %s', (i,))
        item = cursor.fetchone()
        product.append(item)
    return render_template('common/cart.html', cart=cart, product=product)

@endpoint.route('/addcart', methods=['POST'])
@is_loggedin
def addcart():
    data = request.get_json()
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user WHERE user_id = %s', (session['id'],))
    account = cursor.fetchone()
    cart = literal_eval(account['cart'])
    cart[data['product_id']] = data['quantity']
    cursor.execute('UPDATE user SET cart = %s WHERE user_id = %s', (cart, session['id'],))
    cursor.connection.commit()
    return {'cart_no':'1'}

@endpoint.route('/checkout', methods=['GET', 'POST'])
@is_loggedin
def checkout():
    pass

@endpoint.route('/updatecart', methods=['POST'])
@is_loggedin
def updatecart():
    pass

@endpoint.route('/removecart', methods=['POST'])
@is_loggedin
def removecart():
    pass

@endpoint.route('clearcart', methods=['POST'])
@is_loggedin
def clearcart():
    pass
    



