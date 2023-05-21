from flask import Blueprint, render_template, redirect, request, url_for, flash , Flask , Response , session, flash, send_file
from app import app, bcrypt, mysql
import shelve
from app.utils import *
endpoint = Blueprint("ids", __name__)

# @endpoint.before_request
# def migrate():
#     cursor = mysql.connection.cursor()
#     shelvedb = shelve.open('healthcheck_data/healthcheck', 'r')
#     status_dict = shelvedb['status']
#     for dt_string in status_dict:
#         for filename in status_dict[dt_string]:
#             cursor.execute('INSERT INTO')

admin_endpoint_files = ['app/routes/admin/frontpage_ep.py',
                  'app/routes/admin/product_ep.py',
                  'app/routes/admin/user_ep.py',
                  'app/routes/admin/ids_ep.py',
                  'app/routes/admin/admin_ep.py',
                  'app/routes/admin/card_ep.py']
                
endpoint_files = ['app/routes/auth_ep.py',
                  'app/routes/common_ep.py',
                  'app/routes/order_ep.py',
                  'app/routes/reset_ep.py']

admin_file = ['frontpage_ep.py', 'product_ep.py', 'user_ep.py', 'ids_ep.py', 'admin_ep.py', 'card_ep.py']
user_file = ['auth_ep.py', 'common_ep.py', 'order_ep.py', 'reset_ep.py']

@endpoint.route('/ids')
@is_admin
def ids():
    db = shelve.open('healthcheck_data/healthcheck', 'r')
    notif_dict = {}
    for i in endpoint_files:
        notif_dict[i.replace('app/routes/', '')] = len(db[i])
    for i in admin_endpoint_files:
        notif_dict[i.replace('app/routes/admin/', '')] = len(db[i])
    archive_dict = {}
    for i in endpoint_files:
        archive_dict[i.replace('app/routes/', '')] = len(db[i.replace('app/routes/', 'archive-')])
    for i in admin_endpoint_files:
        archive_dict[i.replace('app/routes/admin/', '')] = len(db[i.replace('app/routes/admin/', 'archive-')])
    print(archive_dict)
    # notif_dict = db['notif']
    # incident_dict: dict  = db['incident']
    # print(incident_dict['test'])
    db.close()
    return render_template('admin/ids/ids.html', notif=notif_dict, archive=archive_dict)

# @endpoint.route('/report/<folder>', methods=['GET'])
# def folder(folder):
#     param_filter_date = request.args.get("filter_by_date", type=str, default="")
#     if param_filter_date == "":
#         db = shelve.open('healthcheck_data/healthcheck', 'r')
#         if folder in admin_file:
#             foldername = 'app/routes/admin/'+folder
#         elif folder in user_file:
#             foldername = 'app/routes/'+folder
#         incident_dict = db[foldername]
#     db.close()
#     return render_template('/admin/ids/folder.html', incident_dict=incident_dict, folder=folder)

@endpoint.route('/report/<folder>/<file>', methods=['GET'])
@is_admin
def report(folder, file):
    db = shelve.open('healthcheck_data/healthcheck', 'r')
    if folder in admin_file:
        foldername = 'app/routes/admin/'+folder
    elif folder in user_file:
        foldername = 'app/routes/'+folder
    incident_dict = db[foldername]
    incident_list = incident_dict[file]
    # incident_list = incident_dict[file[0:10]+" "+file[10:]]
    return render_template('/admin/ids/report.html', incident_list=incident_list, folder=folder, file=file)

@endpoint.route('/report/catalog/')
@is_admin
def folder():
    mth = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    """args req"""
    param_filter_folder = request.args.get("filter_by_folder", type=str, default="")
    param_filter_date = request.args.get("filter_by_date", type=str, default="")
    incident_dict: dict = {}

    db = shelve.open('healthcheck_data/healthcheck', 'r')
    if param_filter_folder in admin_file:
        foldername = 'app/routes/admin/'+param_filter_folder
    elif param_filter_folder in user_file:
        foldername = 'app/routes/'+param_filter_folder
    if param_filter_date == "":
        incident_dict = db[foldername]
        month = ''
    elif param_filter_date != "":
        for i in db[foldername]:
            if i[5:7] == param_filter_date:
                incident_dict[i] = db[foldername][i]
        month = mth[param_filter_date]
    db.close()
    return render_template('/admin/ids/folder.html', 
                            incident_dict=incident_dict, 
                            folder=foldername, 
                            param_filter_folder=param_filter_folder,
                            param_filter_date=month)

@endpoint.route('archive/<folder>/<file>', methods=['POST'])
@is_admin
def archivefile(folder, file):
    db = shelve.open('healthcheck_data/healthcheck', 'w')
    if folder in admin_file:
        foldername = 'app/routes/admin/'+folder
    elif folder in user_file:
        foldername = 'app/routes/'+folder
    archive_dict = db['archive-'+folder]
    data = db[foldername][file]
    archive_dict[file] = data
    incident_dict = db[foldername]
    incident_dict.pop(file)
    db['archive-'+folder] = archive_dict
    db[foldername] = incident_dict
    print('this is archive dict', archive_dict)
    print('this is incident dict', incident_dict)
    print(data)
    print('this is folder', 'archive-'+folder)
    print('this is file', file)
    return redirect(url_for('ids.ids'))

# @endpoint.route('/archive')
# @is_admin
# def archive():
#     db = shelve.open('healthcheck_data/healthcheck', 'r')
#     notif_dict = {}
#     for i in endpoint_files:
#         notif_dict[i.replace('app/routes/', '')] = len(db[i.replace('app/routes/', 'archive-')])
#     for i in admin_endpoint_files:
#         notif_dict[i.replace('app/routes/admin/', '')] = len(db[i.replace('app/routes/admin/', 'archive-')])
#     db.close()
#     return render_template('admin/ids/archive.html', notif=notif_dict)

@endpoint.route('/archive/catalog/')
def archive():
    mth = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    """args req"""
    param_filter_folder = request.args.get("filter_by_folder", type=str, default="")
    param_filter_date = request.args.get("filter_by_date", type=str, default="")
    incident_dict: dict = {}

    db = shelve.open('healthcheck_data/healthcheck', 'r')
    if param_filter_folder in admin_file:
        foldername = 'archive-'+param_filter_folder
    elif param_filter_folder in user_file:
        foldername = 'archive-'+param_filter_folder
    if param_filter_date == "":
        incident_dict = db[foldername]
        month = ''
    elif param_filter_date != "":
        for i in db[foldername]:
            if i[5:7] == param_filter_date:
                incident_dict[i] = db[foldername][i]
        month = mth[param_filter_date]
    db.close()
    return render_template('/admin/ids/archivefolder.html', 
                            incident_dict=incident_dict, 
                            folder=foldername, 
                            param_filter_folder=param_filter_folder,
                            param_filter_date=month)

@endpoint.route('/archive/<folder>', methods=['GET'])
@is_admin
def archivefolder(folder):
    db = shelve.open('healthcheck_data/healthcheck', 'r')
    if folder in admin_file:
        foldername = 'archive-'+folder
    elif folder in user_file:
        foldername = 'archive-'+folder
    incident_dict = db[foldername]
    db.close()
    return render_template('/admin/ids/archivefolder.html', incident_dict=incident_dict, folder=folder)

@endpoint.route('/archive/<folder>/<file>', methods=['GET'])
@is_admin
def archivereport(folder, file):
    db = shelve.open('healthcheck_data/healthcheck', 'r')
    if folder in admin_file:
        foldername = 'archive-'+folder
    elif folder in user_file:
        foldername = 'archive-'+folder
    incident_dict = db[foldername]
    incident_list = incident_dict[file]
    # incident_list = incident_dict[file[0:10]+" "+file[10:]]
    return render_template('/admin/ids/archivereport.html', incident_list=incident_list, folder=folder, file=file)

@endpoint.route("/reportxt/<folder>/<file>", methods=["POST"])
@is_admin
def reportxt(folder, file):
    if request.method == "POST":
        db = shelve.open('healthcheck_data/healthcheck', 'r')
        try:
            if folder in admin_file:
                foldername = 'app/routes/admin/'+folder
            elif folder in user_file:
                foldername = 'app/routes/'+folder
            report_dict = db[foldername]
            report_list = report_dict[file]
        except KeyError:
            if folder in admin_file:
                foldername = 'archive-'+folder
            elif folder in user_file:
                foldername = 'archive-'+folder
            report_dict = db[foldername]
            report_list = report_dict[file]
        db.close()
        new_line = '\n'
        lines = []
        print(report_list)
        for key in report_list:
            lines.append(f'{key}{new_line}')
            for line in report_list[key]:
                lines.append(f'{line}{new_line}')
        print(lines)
        return Response(
            lines,
            mimetype="text/plain",
            headers={"Content-Disposition": "attachment; filename="+file+folder+".txt"},
        )