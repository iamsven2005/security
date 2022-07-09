from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file
from app import app, bcrypt, mysql

endpoint = Blueprint("user", __name__)

@endpoint.route('/user')
def user():
    return 'user'