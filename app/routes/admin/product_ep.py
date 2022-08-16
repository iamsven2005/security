from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file
from app import app, bcrypt, mysql
from app.forms import *
from PIL import Image
from uuid import uuid4
import os
from app.utils import *
basedir = os.getcwd()

endpoint = Blueprint("product", __name__)

@endpoint.route('/product')
@is_admin
def product():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product')
    products = cursor.fetchall()
    return render_template('admin/product/product.html', products=products)

@endpoint.route('/addproduct', methods=['GET', 'POST'])
@is_admin
def addproduct():
    form = ProductForm(request.form)
    if request.method == 'POST' and form.validate():
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM product WHERE product_name = %s', (form.productname.data,))
        product = cursor.fetchone()
        if product is None:
            product_id = str(uuid4())[:8]
            cursor.execute('INSERT INTO product VALUES (%s, %s, %s, %s, %s, %s)', (product_id, form.productname.data, form.productdesc.data, form.productprice.data, form.productstock.data, 'Active',))
            cursor.connection.commit()
            img = Image.open(request.files["productimage"])
            img.load()
            img.resize((1200, 600))
            img.convert("RGB")
            img.save(f"{basedir}/app/static/media/product_img/{product_id}.png")
            return redirect(url_for('product.product'))
        else:
            flash('Product Exists', category='error')
            return redirect(request.referrer)
    return render_template('admin/product/product_form.html', form=form)

@endpoint.route('/productdetails/<id>')
@is_admin
def productdetails(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product WHERE product_id = %s', (id,))
    product = cursor.fetchone()
    return render_template('admin/product/productdetails.html', product=product)

# @endpoint.route('/updateproduct/<id>', methods=['GET', 'POST'])
# def updateproduct(id):
#     form = ProductForm(request.form)
#     if request.method == 'POST' and form.validate():
#         cursor = mysql.connection.cursor()
#         cursor.execute('UPDATE product SET WHERE')

@endpoint.route('/deleteproduct/<id>', methods=['POST'])
@is_admin
def deleteproduct(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM product WHERE product_id = %s', (id,))
    cursor.connection.commit()
    return redirect(request.referrer)

@endpoint.route('/status_product/<id>', methods=['POST'])
@is_admin
def product_status(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product WHERE product_id = %s', (id,))
    product = cursor.fetchone()
    if product['product_status'] == 'Active':
        cursor.execute('UPDATE product SET product_status = %s WHERE product_id = %s', ('Inactive', id,))
    else:
        cursor.execute('UPDATE product SET product_status = %s WHERE product_id = %s', ('Active', id,))
    cursor.connection.commit()
    return redirect(request.referrer)

@endpoint.route('/deleteimg/')
def deleteimg():
    filepath = request.args.get('filepath', type=str, default="")
    if filepath != '':
        try:
            if os.path.isfile('app/'+filepath):
                os.remove('app/'+filepath)
            else:
                print('error deleting')
        except:
            print('some error idk')
    else:
        print('error')
    return redirect(request.referrer)