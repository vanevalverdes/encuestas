# -*- coding: utf-8 -*- 
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_from_directory,jsonify,abort
from models.develop.user import User
from utils.packages.application import isPublic,list_class_names, getMenu, getClazzName
from utils.packages.engine import traceError, random, now, send_reset_email
from utils.packages.session import getClazz, saveForm, getORMRecord, requestLog, newQuery
from utils.view_class_container_fields import get_clazz_fields
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from utils.db import db
from flask import session as Session
from models.develop.blob import Blob
from werkzeug.utils import secure_filename
import os

blueprintname = Blueprint("application", __name__)
   
@blueprintname.route('/')
@traceError
def index():
    if current_user.is_authenticated:
        class_names = list_class_names()
        return render_template("backend/index.html",class_names=class_names)
    return render_template('frontend/index.html')
    
@blueprintname.route('/admin/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=username).first()
        
        if user and check_password_hash(user._password_hash, password):
            login_user(user, remember=True)
            usergroup = current_user.usergroup_id
            #menu = getMenu(usergroup)
            #Session["menu"] = menu
            return redirect(url_for('.index'))  # Asumiendo que tienes una ruta 'dashboard'
            #return "Todo en orden"
        elif user:
            flash('Contraseña incorrecta')
        else:
            flash('Email incorrecto')
    return render_template('backend/base/login.html')

@blueprintname.route('/admin/logout/')
@traceError
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))

@blueprintname.route("/application/upload", methods=["POST"])
@traceError
@login_required
def upload_file():

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Crear el record primero (para tener el ID)
    blob = Blob(
        original_name=file.filename,
        mime_type=file.mimetype,
        size=len(file.read())
    )
    file.seek(0)  # Volvemos al inicio del stream para guardarlo
    db.session.add(blob)
    db.session.commit()

    # Crear carpeta uploads/<id>/
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], str(blob.id))
    os.makedirs(folder, exist_ok=True)

    # Guardar archivo con su nombre original (o seguro)
    filename = secure_filename(file.filename)
    filepath = os.path.join(folder, filename)
    file.save(filepath)

    return jsonify({"id": blob.id, "filename": filename})

@blueprintname.route("/blob/get/<int:blob_id>")
@login_required  
def get_blob(blob_id):
    # Buscar el blob
    blob = Blob.query.get(blob_id)
    if not blob:
        abort(404, "Archivo no encontrado")

    # --- PERMISOS ---
    # Aquí debes decidir tu lógica de permisos. Ejemplo:
    # Solo el dueño del objeto relacionado puede descargar.
    # (esto depende de cómo relaciones Object con User en tu app)
    if not user_can_access(blob):
        abort(403, "No tienes permisos para acceder a este archivo")

    # Construir ruta a carpeta
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], str(blob.id))
    filepath = os.path.join(folder, blob.original_name)

    if not os.path.exists(filepath):
        abort(404, "Archivo no encontrado en el servidor")

    # Enviar el archivo de forma segura
    return send_from_directory(
        directory=folder,
        path=blob.original_name,
        as_attachment=True  # fuerza descarga
    )

def user_can_access(blob):
    return current_user.is_authenticated

@blueprintname.route("/blob/read/<int:blob_id>")
@login_required
def get_blob_read(blob_id):
    # Buscar el blob
    blob = Blob.query.get(blob_id)
    if not blob:
        abort(404, "Archivo no encontrado")

    # --- Permisos ---
    if not user_can_access(blob):
        abort(403, "No tienes permisos para acceder a este archivo")

    # Ruta física al archivo
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], str(blob.id))
    filepath = os.path.join(folder, blob.original_name)

    if not os.path.exists(filepath):
        abort(404, "Archivo no encontrado en el servidor")

    # Enviar la imagen para que el navegador la muestre
    return send_from_directory(
        directory=folder,
        path=blob.original_name,
        as_attachment=False  
    )

@blueprintname.route("/blob/thumbnail/<int:blob_id>")
@login_required
def get_thumbnail(blob_id):
    # Buscar el blob
    blob = Blob.query.get(blob_id)
    if not blob:
        abort(404, "Archivo no encontrado")

    # --- Permisos ---
    if not user_can_access(blob):
        abort(403, "No tienes permisos para acceder a este archivo")

    # Ruta física al archivo
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], str(blob.id))
    filepath = os.path.join(folder, blob.original_name)

    if not os.path.exists(filepath):
        abort(404, "Archivo no encontrado en el servidor")

    # Enviar la imagen para que el navegador la muestre
    if blob.mime_type.startswith("image/") and blob.original_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
        from PIL import Image
        size = (200, 200)
        im = Image.open(filepath)
        im.thumbnail(size)
        thumb_path = os.path.join(folder, f"thumb_{blob.original_name}")
        im.save(thumb_path)
        return send_from_directory(
            directory=folder,
            path=f"thumb_{blob.original_name}",
            as_attachment=False  
        )
    else:
        return send_from_directory(
            directory=os.path.join(current_app.config["STATIC_FOLDER"], "assets", "img"),
            path=f"document.png",
            as_attachment=False  
        )

@blueprintname.route("/application/edit-row/", methods=["POST"])
@login_required
def get_edit_row():
    from utils.packages.session import getORMRecord
    from utils.packages.application import getClazzName
    import uuid
    # Accede al JSON del cuerpo de la petición
    data = request.json
    
    # Extrae los valores del JSON
    table_id = int(data.get('table_id'))
    record_id = int(data.get('record_id'))
    originRequest = data.get('origin')
    if originRequest:
        val = originRequest.split(":")
        frClassname = getClazzName(int(val[2]))
        origin = {}
        origin["fieldName"] = val[0]
        origin["value"] = getORMRecord(frClassname, val[1])
        origin["tableId"] = int(val[2])
    else:
        origin = False

    fields_raw = data.get('fields')

    if fields_raw == "False":
        fields = False
        
    elif fields_raw:
        fields = [f.strip() for f in fields_raw]
        print(f"fields: {fields}")
    else:
        fields = False
    
    # Asegúrate de que los datos existen antes de renderizar la plantilla
    if not table_id or not record_id:
        return jsonify({"error": "Missing table_id or record_id"}), 400
    
    Record = getORMRecord(getClazzName(int(table_id)), int(record_id))
    uuidStr = str(random())
    #print(f"uuidStr: {uuidStr}")
    ##print(f"Rendering new row for table_id: {table_id} with fields: {fields}")
    return render_template("backend/snippets/editRow.html", fields=fields, table_id=table_id,uuid=uuidStr, record=Record, origin=origin)

@blueprintname.route("/application/new-row/", methods=["POST"])
@login_required
def get_new_row():
    from utils.packages.session import getORMRecord
    from utils.packages.application import getClazzName
    import uuid
    # Accede al JSON del cuerpo de la petición
    data = request.json
    
    # Extrae los valores del JSON
    table_id = int(data.get('table_id'))
    fields = data.get('fields')
    originRequest = data.get('origin')
    if originRequest:
        val = originRequest.split(":")
        frClassname = getClazzName(int(val[2]))
        origin = {}
        origin["fieldName"] = val[0]
        origin["value"] = getORMRecord(frClassname, val[1])
        origin["tableId"] = int(val[2])
    else:
        origin = False

    # Asegúrate de que los datos existen antes de renderizar la plantilla
    if not table_id :
        return jsonify({"error": "Missing table_id"}), 400
    if fields == "False":
        fields = False
    uuidStr = str(random())
    print(f"uuidStr: {uuidStr}")
    ##print(f"Rendering new row for table_id: {table_id} with fields: {fields}")
    return render_template("backend/snippets/newRow.html", fields=fields, table_id=table_id,uuid=uuidStr, origin=origin)

@blueprintname.route(f'/application/save-row/', methods=["POST"])
@traceError
@login_required
def save_row():
    data = request.form
    if data.get("fields_in_request"):
        fields_raw = data.get('fields_in_request')

        if fields_raw == "False":
            fields = False
            
        elif fields_raw:
            fields = [f.strip() for f in fields_raw.split(',')]
            print(f"fields: {fields}")
    else:
        fields = False

    originRequest = data.get('origin')
    if originRequest:
        origin = originRequest
    else:
        origin = False
        
    classid = int(data.get("clazznameRecord"))  
    classname = getClazzName(classid)
    fieldsRecord = get_clazz_fields(classname)
    if data.get("id"):
        Record = getORMRecord(classname, int(data.get("id")))
        print(f"Editando: {Record}")
    else:
        modelClass = getClazz(classname)
        # Uso de la clase importada
        Record = modelClass()
    Record = saveForm(Record,fieldsRecord)
    db.session.commit()
    print(f"Guardado: {Record}")
    return render_template("backend/snippets/rowRead.html", fields=fields, table_id=classid, record=Record,origin=origin)

@blueprintname.route(f'/application/get-row/<int:table_id>/<int:record_id>', methods=["GET"])
@traceError
@login_required
def get_row(table_id, record_id):
    classid = table_id 
    
    # Obtener campos opcionales (si se pasaran por query string: ?fields_in_request=a,b)
    fields_raw = request.args.get('fields_in_request') 
    
    if fields_raw:
        if fields_raw.lower() == "false":
            fields = False
        else:
            fields = [f.strip() for f in fields_raw.split(',')]
            print(f"fields: {fields}")
    else:
        fields = False

    origin = request.args.get('origin', False)

    classname = getClazzName(classid)
    Record = getORMRecord(classname, record_id)
    print(f"Visualizando: {Record}")
    return render_template("backend/snippets/rowRead.html", fields=fields, table_id=classid, record=Record,origin=origin)

@blueprintname.route(f'/application/delete-row/', methods=["POST"])
@traceError
@login_required
def delete_row():
    data = request.get_json()
    print(f"Data recibida para eliminar: {data}")
    print({key: data[key] for key in data})
    void = requestLog(data)
    classid = int(data.get("table_id"))
    classname = getClazzName(classid)
    if data.get("record_id"):
        record = getORMRecord(classname, int(data.get("record_id")))
        print(f"Editando: {record}")
    db.session.delete(record)
    db.session.commit()
    print(f"Eliminado: {record}")
    return jsonify({"success": True})

@blueprintname.route(f'/application/action/', methods=["GET","POST"])
@traceError
@login_required
def get_action():
    import ast

    if request.method == "GET":
        classid = request.args.get('export')
        rowList = request.args.getlist('rowId')
        table_size = request.args.getlist('total')
        classfields = get_clazz_fields(classid)

        if classid:
            return render_template("backend/interface/exportSelectFields.html", rowList=rowList, list_size=len(rowList), classid=classid, table_size=table_size, classfields=classfields)
        else:
            return "Error: Los datos recibidos no son válidos.", 400
    else:
        classid = request.form.get("classid")
        export_scope = request.form.get("export_scope")

        if export_scope == "all_data":
            query = newQuery(classid)
            table = query.getRecordsFromSession()
        else:
            objList = request.form.getlist("rowList")

            if objList:
                strList = objList[0] 
                
                try:
                    lista_de_strings = ast.literal_eval(strList)
                    
                    # 4. Convertir cada ID a entero
                    lista_de_enteros = [int(item) for item in lista_de_strings]
                    
                except (ValueError, SyntaxError) as e:
                        # Esto captura errores si la cadena no es una lista válida de Python
                        print(f"Error al evaluar la estructura de datos: {e}")
                        lista_de_enteros = []
                    
            
            query = newQuery(classid)
            table = query.getRecords(lista_de_enteros)
        
        formatExport = request.form.get("format")
        fieldsExport = request.form.getlist("addedFields_hidden")
        print(fieldsExport)
        classfields = get_clazz_fields(classid)
        headers = []
        for field in fieldsExport:
            try:
                field_data = classfields[field]
                headers.append(field_data.get("label", field))
            except:
                pass
        print(headers)

        if formatExport == "csv":
            from utils.packages.engine import toCSV
            file = toCSV(table,headers,fieldsExport)
            return file
        if formatExport == "pdf":
            from utils.packages.engine import toPdf
            filename = f"export_{getClazzName(classid)}"
            html = render_template("backend/export/table.html", table=table,headers=headers,fields=fieldsExport,classfields=classfields)
            pdfUrl = toPdf(html, filename)
            print(f"PDF generated and saved at {pdfUrl}")
                # Enviar el archivo de forma segura
            return send_from_directory(
                directory=pdfUrl[0],
                path=pdfUrl[1],
                as_attachment=True  # fuerza descarga
            )

        else:
            return "Export generation failed"

        

@blueprintname.route('/admin/reset-password/', methods=["GET", "POST"])
def reset_password_request():
    if request.method == "POST":
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(user.email, salt="asd;ljasll2asdas")
            user._reset_token = token
            user._token_expiration = now() + timedelta(hours=1)
            db.session.commit()
            link = url_for('.reset_password', token=token, _external=True)
            send_reset_email(user.email, link)
            flash('An email has been sent with instructions to reset your password.', 'info')
        else:
            flash('Email address not found.', 'danger')
        return redirect(url_for('.reset_password_request'))
    return render_template("frontend/reset_password_request.html")

@blueprintname.route('/admin/reset-password/<token>', methods=["GET", "POST"])
def reset_password(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='asd;ljasll2asdas', max_age=3600)  # 1 hour validity
    except:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('.reset_password_request'))
    
    user = User.query.filter_by(email=email).first()
    if not user or user._reset_token != token:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('.reset_password_request'))
    
    if request.method == "POST":
        password = request.form.get("password")
        user.set_password(password)
        user._reset_token = None  # Invalidate the token
        user._token_expiration = None
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('application.login'))  # Redirigir a la página de inicio de sesión

    return render_template("frontend/reset_password.html", token=token)