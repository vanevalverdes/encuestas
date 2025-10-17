
from utils.view_class_container_fields import get_clazz_fields
from utils.packages import application, session, engine
from utils.packages.relevant import verify_relevant
from utils.packages.engine import traceError
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from utils.db import db
from werkzeug.utils import secure_filename
import os
import threading


blueprintname = Blueprint("routing", __name__)
slug = "admin"

@blueprintname.route(f'/{slug}/<int:classid>/new/', methods=["GET","POST"])
@traceError
@verify_relevant('create')
@login_required
def create_record(classid):
    class_names = application.list_class_names()
    classname = application.get_class_name(classid)
    classnameLabel = application.get_class_name_label(classid)
    fields = get_clazz_fields(classid)
    #print(fields)
    templateName = application.get_template(classid)
    template = f"{templateName}.html" if templateName else None


    # Deshabilitar containers con tabs
    #has_tabs = any(container['type'] == 'tab' for container in containers.values())
    ##print(containers)
    if request.method == "GET":
        session.updateHistory()
        backlink = session.getBackUrl(classid)
        originRequest = request.args.get('origin')
        if originRequest:
            val = originRequest.split(":")
            frClassname = application.getClazzName(val[1])
            origin = {}
            origin["fieldName"] = val[0]
            origin["value"] = session.getORMRecord(frClassname, val[2])
        else:
            origin = False
        if template:
            template_path = os.path.join(current_app.root_path, 'templates', 'backend', 'custom', template)
            if os.path.exists(template_path):
                template = f"backend/custom/{template}"
                return render_template(template, classnameLabel=classnameLabel,  editable=True, fields=fields, classname=classname, classid=classid, origin=origin, backlink=backlink, class_names=class_names)
        else:
            return render_template("backend/routing/base.html", classnameLabel=classnameLabel,  editable=True, fields=fields, classname=classname, classid=classid, origin=origin, backlink=backlink, class_names=class_names)

    elif request.method == "POST":
        session.updateHistory(-1)
        backlink = session.getBackUrl(classid)
        modelClass = session.getClazz(classname)
        # Uso de la clase importada
        Record = modelClass()
        session.saveForm(Record,fields)
        db.session.add(Record)
        db.session.commit()

        return redirect(url_for('.edit_record', record_id=Record.id,classid=classid,backlink=backlink))
    

@blueprintname.route(f'/{slug}/<int:classid>/<int:record_id>/')
@traceError
@verify_relevant('read')
@login_required
def view_record(classid,record_id):
    extraActions= False
    
    class_names = application.list_class_names()
    classname = application.get_class_name(classid)
    fields = get_clazz_fields(classid)
    templateName = application.get_template(classid)
    template = f"{templateName}.html" if templateName else None
    cmd = request.args.get('cmd')
    if cmd == "stop":
        session.updateHistory(-1)
    else:
        session.updateHistory()
    backlink = session.getBackUrl(classid)
    record = session.getORMRecord(classname, record_id)
    if template:
        template_path = os.path.join(current_app.root_path, 'templates', 'backend', 'custom', template)
        if os.path.exists(template_path):
            template = f"backend/custom/{template}"
            return render_template(template, record=record,editable=False,backlink=backlink, fields=fields,classname=classname, class_names=class_names,classid=classid)
    return render_template('backend/routing/base.html', record=record,editable=False,backlink=backlink, fields=fields,classname=classname, class_names=class_names,classid=classid)


@blueprintname.route(f'/{slug}/<int:classid>/<int:record_id>/edit/', methods=['GET', 'POST'])
@traceError
@verify_relevant('edit')
@login_required
def edit_record(classid,record_id):
    class_names = application.list_class_names()
    classname = application.get_class_name(classid)
    fields = get_clazz_fields(classid)
    #print(fields)
    templateName = application.get_template(classid)
    template = f"{templateName}.html" if templateName else None
    record = session.getORMRecord(classname, record_id)

    if request.method == 'POST':
        session.updateHistory()
        backlink = session.getBackUrl(classid)
        void = session.saveForm(record,fields)
        db.session.commit()
        flash('El registro ha sido actualizada exitosamente.', 'success')
        if template:
            template_path = os.path.join(current_app.root_path, 'templates', 'backend', 'custom', template)
            if os.path.exists(template_path):
                template = f"backend/custom/{template}"
                return render_template(template, record=record,editable=True,backlink=backlink, fields=fields,classname=classname, class_names=class_names,classid=classid)
        else:
            return render_template('backend/routing/base.html', record=record,editable=True,backlink=backlink, fields=fields,classname=classname, class_names=class_names,classid=classid)
    session.updateHistory()
    backlink = session.getBackUrl(classid)
    if template:
        template_path = os.path.join(current_app.root_path, 'templates', 'backend', 'custom', template)
        if os.path.exists(template_path):
            template = f"backend/custom/{template}"
            return render_template(template, record=record,editable=True,backlink=backlink, fields=fields,classname=classname, class_names=class_names,classid=classid)
    else:
        return render_template('backend/routing/base.html', record=record,editable=True,backlink=backlink, fields=fields,classname=classname, class_names=class_names,classid=classid)

@blueprintname.route(f'/{slug}/<int:classid>/<int:record_id>/delete/', methods=['POST'])
@traceError
@verify_relevant('delete')
@login_required
def delete_record(classid,record_id):
    void = session.requestLog(request.form)
    classname = application.get_class_name(classid)
    record = session.getORMRecord(classname, record_id)
    
    backlink = session.getBackUrl(classid)

    db.session.delete(record)
    db.session.commit()
    flash('El registro ha sido eliminada exitosamente.', 'success')
    if backlink:
        return redirect(backlink)  # Asumiendo que existe una ruta para listar instituciones
    return redirect(url_for('.list_record',classid=classid,page=1))  # Asumiendo que existe una ruta para listar instituciones

@blueprintname.route(f'/{slug}/<int:classid>/page/<int:page>/')
@traceError
@verify_relevant('read')
@login_required
def list_record(classid,page):
    session.updateHistory()
    print(request.args)
    record = application.getClazz(int(classid))
    print(record)
    sortData = record.getSortField()
    #print(sortData)
    if sortData:
        sortData = sortData.split('|')
        sortField = sortData[0]
        sort = sortData[1]
    if not sortField:
        sortField = "id"
        
    if not sort:
        sort = "desc"
    print(classid)
    query = session.filterTableView(int(classid))
    
    print(query)
    sort_field = request.args.get('sort_field')
    sort_dir = request.args.get('sort_dir')
    if sort_field and sort_dir:
        query.sortBy(sort_field,sort_dir)
    else:
        query.sortBy(sortField,sort)
    query.toSession()
    table = query.pagination(int(page),20)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    #print(table)
    #records = table  # Consulta todas las instituciones
    if is_ajax:
        return render_template('backend/snippets/tableBody.html', table=table, classid=classid)
    else:
        return render_template('backend/routing/list_base.html',table=table,classid=classid)

@blueprintname.route(f'/{slug}/getTable/<int:classid>')
@traceError
@verify_relevant('read')
@login_required
def get_table(classid):
    from flask import jsonify, abort
    # 1. Recibir parámetros de DataTables (limpios por el JS)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    sort_field = request.args.get('sort_field', 'id')
    sort_dir = request.args.get('sort_dir', 'asc')
    draw = int(request.args.get('draw', 1)) # Parámetro de seguridad/sincronización de DataTables

    try:
        # Obtener la clase del modelo (ej. Object, Measurement)
        record = application.getClazz(classid)
    except:
        return jsonify({"error": "Modelo no encontrado"}), 404
        
    # 2. Construir la consulta base (incluyendo filtros si los tienes)
    query = session.newQuery(classid) 
    
    # 3. Aplicar la ordenación antes de paginar
    query.sortBy(sort_field,sort_dir)

    # 4. Aplicar la paginación
    table = query.pagination(page,10)
    # 5. Formatear los datos para DataTables
    data = []
    for item in table.items:
        data.append(engine.tableToDict(item))

    # 6. Devolver el JSON en el formato específico de DataTables
    response = {
        "draw": draw,
        "recordsTotal": table.total, 
        "recordsFiltered": table.total, # Si no hay filtrado, es el total
        "data": data
    }
    return jsonify(response)


@blueprintname.route(f'/{slug}/<int:classid>/export/')
@traceError
@login_required
def export_record(classid):
    from utils.packages import exporter
    record = application.getClazz(classid)
    # Obtiene Configuración de tabla
    tableFields = {}
    if record.getDisplayFields():
        for line in record.getDisplayFields().split(","):
            parts = line.split("|")
            tableFields[parts[0]] = parts[1]
    else:
        tableFields["#"] = "id"
    
    headers = tableFields
    fields = tableFields
    
    return exporter.exportCSV(classid, headers, fields)
