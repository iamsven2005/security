from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file
from app import app, bcrypt, mysql
from app.utils import  *

endpoint = Blueprint("admin", __name__)

@endpoint.route('/frontpage')
@is_admin
def frontpage():
    return render_template('admin/frontpage.html')