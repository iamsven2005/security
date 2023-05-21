from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file
from app import app, bcrypt, mysql
from datetime import datetime, timedelta
from app.forms import *
from app.utils import  *
from uuid import uuid4

endpoint = Blueprint("user", __name__)

@endpoint.route('/user')
@is_admin
def user():
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
    return render_template('admin/user/user.html', users = users, activity=activity)

@endpoint.route('/userManager')
@is_admin
def userManager():
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
    return render_template('admin/userManager/user_manager.html', users = users, activity=activity)

@endpoint.route('/updateUser/<id>', methods=['GET', 'POST'])
@is_admin
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

@endpoint.route('/disabled/<id>', methods=['POST'])
@is_admin
def disabled(id):
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE user SET  Activation = %s WHERE user_id = %s', ['no',id])
    cursor.connection.commit()
    return redirect(request.referrer)

@endpoint.route('/activated/<id>', methods=['POST'])
@is_admin
def activated(id):
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE user SET  Activation = %s WHERE user_id = %s', ['yes',id])
    cursor.connection.commit()
    return redirect(request.referrer)