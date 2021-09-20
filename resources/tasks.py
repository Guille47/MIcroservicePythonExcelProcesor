from flask import request, jsonify, Blueprint
from datetime import datetime
import os
import urllib.request
from werkzeug.utils import secure_filename
from database import tasks
import pandas as pd

UPLOAD_FOLDER = "files/"
ALLOWED_EXTENSIONS = set(['xlsx'])

tasks_bp = Blueprint('routes-tasks', __name__)

# @tasks_bp.route('/tasks', methods=['POST'])
# def add_task():
#     title = request.json['title']
#     created_date = datetime.now().strftime("%x") # 5/22/2021

#     data = (title, created_date)
#     task_id = tasks.insert_task(data)

#     if task_id:
#         task = tasks.select_task_by_id(task_id)
#         return jsonify(task)
#     return jsonify({'message': 'Internal Error'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @tasks_bp.route('/tasks/withFile', methods=['POST'])
# def add_task_with_excel():
#     # Verificando si el archivo esta o no esta en el parametro de request de flask
#     if 'files[]' not in request.files:
#         resp = jsonify({'message' : 'No file part in the request'})
#         resp.status_code = 400
#         return resp
#     # Creando una nueva lista del parametro de archivos
#     files = request.files.getlist('files[]')
#     errors = {}
#     success = False
#     # iterando la lista de archivos para detectar los archivos que vienen en esta
#     for file in files: 
#         # Verificando si la extencion del archivo esta en la lista de archivos admitidos  
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(UPLOAD_FOLDER , filename))
#             success = True
#         else:
#             errors[file.filename] = 'File type is not allowed'
#     if success and errors:
#         errors['message'] = 'File(s) successfully uploaded'
#         resp = jsonify(errors)
#         resp.status_code = 500
#         return resp
#     if success:
#         resp = jsonify({'message' : 'Files successfully uploaded'})
#         resp.status_code = 201
#         return resp
#     else:
#         resp = jsonify(errors)
#         resp.status_code = 500
#         return resp

@tasks_bp.route('/tasks/withFile', methods=['POST'])
def add_task_with_excel():
    # Verificando si el archivo esta o no esta en el parametro de request de flask
    filePath = ''
    if 'files[]' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    # Creando una nueva lista del parametro de archivos
    files = request.files.getlist('files[]')
    errors = {}
    success = False
    # iterando la lista de archivos para detectar los archivos que vienen en esta
    for file in files: 
        # Verificando si la extencion del archivo esta en la lista de archivos admitidos  
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filePath = os.path.join(UPLOAD_FOLDER , filename)
            file.save(filePath)
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'
    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        data = pd.read_excel(filePath)
        data = pd.DataFrame(data)
        data = data.to_json(date_format='iso',orient="records")
        resp = data
        # resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp

@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    data = tasks.select_all_tasks()

    if data:
        return jsonify({'tasks': data})
    elif data == False:
        return jsonify({'message': 'Internal Error'})
    else:
        return jsonify({'tasks': {}})

@tasks_bp.route('/tasks', methods=['PUT'])
def update_task():
    title = request.json['title']
    id_arg = request.args.get('id')

    if tasks.update_task(id_arg, (title,)):
        task = tasks.select_task_by_id(id_arg)
        return jsonify(task)
    return jsonify({'message': 'Internal Error'})

@tasks_bp.route('/tasks', methods=['DELETE'])
def delete_task():
    id_arg = request.args.get('id')

    if tasks.delete_task(id_arg):
        return jsonify({'message': 'Task Deleted'})
    return jsonify({'message': 'Internal Error'})


@tasks_bp.route('/tasks/completed', methods=['PUT'])
def complete_task():
    id_arg = request.args.get('id')
    completed = request.args.get('completed')

    if tasks.complete_task(id_arg, completed):
        return jsonify({'message': 'Succesfully'})
    return jsonify({'message': 'Internal Error'})