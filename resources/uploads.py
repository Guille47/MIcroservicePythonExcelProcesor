from flask import request, jsonify, Blueprint
import os
import urllib.request
from werkzeug.utils import secure_filename
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('sqlite:///database/sql/uploads.db', echo=False)

UPLOAD_FOLDER = "files/"
ALLOWED_EXTENSIONS = set(['xlsx'])

uploads_bp = Blueprint('routes-uploads', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@uploads_bp.route('/uploads', methods=['POST'])
def add_uploads_with_excel():
    # Verificando si el archivo esta o no esta en el parametro de request de flask
    filename = ''
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
        filename = os.path.splitext(filename)[0]
        data.to_sql(filename, con=engine, if_exists='replace')
        os.remove(filePath)
        return jsonify({'message': 'File inserted succesfully in the table' + filename})
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp