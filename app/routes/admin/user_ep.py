from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file
from app import app, bcrypt, mysql
from app.forms import *

endpoint = Blueprint("user", __name__)

@endpoint.route('/user')
def user():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    return render_template('admin/user/user.html', users = users)

@endpoint.route('/userManager')
def userManager():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    return render_template('admin/userManager/user_manager.html', users = users)

@endpoint.route('/updateUser/<id>', methods=['GET', 'POST'])
def updateUser(id):
    form = AdminForm(request.form)
    cursor = mysql.connection.cursor()
    if request.method == 'POST' and form.validate():
        cursor.execute('SELECT * FROM user WHERE user_id = %s', [id])
        updateAdmin = cursor.fetchone()
        if updateAdmin:
            try:
                hashpwd = bcrypt.generate_password_hash(form.password.data)
                cursor.execute('UPDATE user SET  username = %s, password = %s, email = %s,status = %s, role = %s WHERE user_id = %s' ,
                                [form.username.data, hashpwd,form.email.data, form.status.data, form.role.data, id])
                mysql.connection.commit()
                flash('Account has been added', category='success')
            except:
                flash("There is already a same email in the database.", category='error')
        else:
            flash("There is already a same email in the database.", category='error')
        return redirect(url_for('user.user'))
    return render_template('admin/user/add_user.html', form=form)