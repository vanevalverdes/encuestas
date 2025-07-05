
from utils.view_class_container_fields import get_clazz_fields
from utils.methods import application, session, engine
from utils.methods.relevant import verify_relevant
from utils.methods.engine import traceError
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from utils.db import db
from werkzeug.utils import secure_filename
import os
import threading


blueprintname = Blueprint("rounting", __name__)
slug = "admin"

@blueprintname.route(f'/{slug}/<int:classid>/new/', methods=["GET","POST"])
@traceError
@verify_relevant('create')
@login_required
def create_record(classid):
    class_names = application.list_class_names()
    classname = application.get_class_name(classid)
    classnameLabel = application.get_class_name_label(classid)
    containers = get_clazz_fields(classid)
    backlink = request.args.get("backlink")

    has_tabs = any(container['type'] == 'tab' for container in containers.values())
    #print(containers)
    if request.method == "GET":
        foreignrecord = request.args.get('foreignrecord')
        if foreignrecord:
            val = foreignrecord.split(":")
            foreignRecord = {}
            foreignRecord["fieldName"] = val[0]
            foreignRecord["value"] = val[1]
        else:
            foreignRecord = False
        return render_template("backend/routing/new_base.html", has_tabs=has_tabs,classnameLabel=classnameLabel,containers=containers,classname=classname,classid=classid,foreignrecord=foreignRecord,backlink=backlink)
    elif request.method == "POST":
            
        modelClass = session.getClazz(classname)
        # Uso de la clase importada
        Record = modelClass()
        session.saveForm(Record,containers)
        db.session.add(Record)
        db.session.commit()

        return redirect(url_for('.edit_record', record_id=Record.id,has_tabs=has_tabs,classname=classname, class_names=class_names,classid=classid,backlink=backlink))
    

@blueprintname.route(f'/{slug}/<int:classid>/<int:record_id>/')
@traceError
@verify_relevant('read')
@login_required
def view_record(classid,record_id):
    if classid == 1:
        transcribe = f"/{slug}/{classid}/{record_id}/transcribe/"
        write = f"/{slug}/{classid}/{record_id}/write/"
        transcribeandwrite = f"/{slug}/{classid}/{record_id}/transcribeandwrite/"
        extraActions = [
            {"typeBtn":"dropdown","title":"Procesar archivo","options":[
                {"option":"Transcribir",
                 "url":transcribe},
                {"option":"Escribir artículo",
                 "url":write},
                {"option":"Transcribir y escribir artículo",
                 "url":transcribeandwrite}
            ]
            }
        ]
    else:
        extraActions= False

    class_names = application.list_class_names()
    classname = application.get_class_name(classid)
    containers = get_clazz_fields(classid)
    backlink = request.args.get("backlink")
    print(containers.values())
    has_tabs = any(container['type'] == 'tab' for container in containers.values())
    #print(containers)

    institution = session.getORMRecord(classname, record_id)
    # Consulta tablas conectadas
    connectedTables = {}
    for key, container in containers.items():
        if container['connected_table']:
            tableId = container['connected_table']
            clazzConnectedRecord = application.getClazzDetails(container['connected_table'])
            clazzConnectedName = clazzConnectedRecord.getName()
            clazzConnectedLabel = clazzConnectedRecord.getLabel()

            # Obtener el nombre del campo de conexión 
            clazzConnectedFields = clazzConnectedRecord.getFields()
            moneyFieldConnected = []
            for fi in clazzConnectedFields:
                if fi.type == "connected_table" and fi.connected_table == classid:
                    parentFieldName = fi.name
                if fi.type == "Money":
                    moneyFieldConnected.append(fi.name)
            
            # Obtiene records conectados        
            record = session.getRecord(classname,record_id)
            tableRecords = record.getConnectedTable(clazzConnectedName)
            
            # Obtiene Configuración de tabla
            tableFields = {}
            #print(container["connected_table_fields"])
            for line in container["connected_table_fields"].split(","):
                parts = line.split("|")
                tableFields[parts[0]] = parts[1]
            
            #print(tableRecords)
            connectedTables[tableId] = {
                'class_name': clazzConnectedName,
                'class_label': clazzConnectedLabel,
                'parent_field': parentFieldName,
                'records': tableRecords,
                'connected_table_fields': tableFields,
                'moneyFieldConnected': moneyFieldConnected,
            }
    fieldsMoneyFields = engine.moneyValuesToView(containers,institution)
    #print(backlink)
    return render_template('backend/routing/view_base.html',has_tabs=has_tabs,extraActions=extraActions, institution=institution,fieldsMoneyFields=fieldsMoneyFields,backlink=backlink, containers=containers,classname=classname, class_names=class_names,classid=classid,connectedTables=connectedTables)

@blueprintname.route(f'/{slug}/<int:classid>/<int:record_id>/edit/', methods=['GET', 'POST'])
@traceError
@verify_relevant('edit')
@login_required
def edit_record(classid,record_id):
    class_names = application.list_class_names()
    classname = application.get_class_name(classid)
    containers = get_clazz_fields(classid)
    institution = session.getORMRecord(classname, record_id)
    backlink = request.args.get("backlink")
    has_tabs = any(container['type'] == 'tab' for container in containers.values())
    fieldsMoneyFields = engine.moneyValuesToView(containers,institution)
    if request.method == 'POST':
        session.saveForm(institution,containers)
        db.session.commit()
        flash('El registro ha sido actualizada exitosamente.', 'success')
        fieldsMoneyFields = engine.moneyValuesToView(containers,institution)
        return render_template('backend/routing/edit_base.html',has_tabs=has_tabs, institution=institution,fieldsMoneyFields=fieldsMoneyFields,backlink=backlink, containers=containers,classname=classname, class_names=class_names,classid=classid)
    return render_template('backend/routing/edit_base.html',has_tabs=has_tabs, institution=institution,fieldsMoneyFields=fieldsMoneyFields,backlink=backlink,containers=containers,classname=classname, class_names=class_names,classid=classid)

@blueprintname.route(f'/{slug}/<int:classid>/<int:record_id>/delete/', methods=['POST'])
@traceError
@verify_relevant('delete')
@login_required
def delete_record(classid,record_id):
    classname = application.get_class_name(classid)
    institution = session.getORMRecord(classname, record_id)
    backlink = request.args.get("backlink")

    db.session.delete(institution)
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
    from models.develop.user import User
    users = User.query.filter(User.usergroup_id != 1).all()

    class_names = application.list_class_names()
    classname = application.get_class_name(classid)
    classnameLabel = application.get_class_name_label(classid)
    record = application.getClazzDetails(classid)
    sortData = record.getSortField()
    if sortData:
        sortData = sortData.split('|')
        sortField = sortData[0]
        sort = sortData[1]
    else:
        sortField = "id"
        sort = "desc"

    moneyFields = application.getClazzMoneyFields(classname)
    dateFields = application.getClazzDateFields(classname)


    # Obtiene Configuración de tabla
    tableFields = {}
    if record.getDisplayFields():
        for line in record.getDisplayFields().split(","):
            parts = line.split("|")
            tableFields[parts[0]] = parts[1]
    else:
        tableFields["#"] = "id"

    # Obtiene Configuración de busqueda
    searchFields = []
    if record.getSearchFields():
        for line in record.getSearchFields().split(","):
            searchFields.append(line)
    else:
        searchFields.append("id")
        
    searchFields = record.displaySearchFields(searchFields)
    
    query = session.filterTableView(classname)
    query.sortBy(sortField,sort)
    table = query.pagination(page,10)
    #institutions = table  # Consulta todas las instituciones
    
    
    return render_template('backend/routing/list_base.html',users=users,moneyFields=moneyFields,classnameLabel=classnameLabel,dateFields=dateFields, table=table,classname=classname,class_names=class_names,classid=classid,table_fields=tableFields,searchFields=searchFields)


@blueprintname.route(f'/{slug}/<int:classid>/export/')
@traceError
@login_required
def export_record(classid):
    from utils import exporter
    
    headers = ['ID', 'Status', 'Tipo', 'Agencia', 'Nombre','Apellido', 'Monto', 'Fecha Reserva', 'Detalle', 'Usuario', 'Fecha Compra']
    fields = ['id', 'statusOrder', 'typeSource', 'agency', 'name','lastname', 'amount', 'dateReservation', 'comment', 'createdby', 'created_at']
    
    return exporter.exportCSV(classid, headers, fields)

#################################################################################

@blueprintname.route(f'/survey/<int:record_id>/', methods=["GET","POST"])
@traceError
@login_required
def survey(record_id):
    class_names = application.list_class_names()
    classname = application.get_class_name(record_id)
    classnameLabel = application.get_class_name_label(record_id)
    containers = get_clazz_fields(record_id)

    #print(containers)
    if request.method == "GET":
        return render_template("backend/survey.html")
    elif request.method == "POST":
            
        modelClass = session.getClazz(classname)
        # Uso de la clase importada
        Record = modelClass()
        session.saveForm(Record,containers)
        db.session.add(Record)
        db.session.commit()
        flash('Se guardó correctamente la encuesta. Puedes ingresar una nueva.', 'success')
        return render_template("backend/survey.html",success=True)
    
@blueprintname.route(f'/boca-urna-pln/', methods=["GET","POST"])
@traceError
@login_required
def pln_day():
    record_id = 4
    class_names = application.list_class_names()
    classname = application.get_class_name(record_id)
    classnameLabel = application.get_class_name_label(record_id)
    containers = get_clazz_fields(record_id)

    #print(containers)
    if request.method == "GET":
        return render_template("backend/pln-day.html")
    elif request.method == "POST":
            
        modelClass = session.getClazz(classname)
        # Uso de la clase importada
        Record = modelClass()
        session.saveForm(Record,containers)
        db.session.add(Record)
        db.session.commit()
        flash('Se guardó correctamente la encuesta. Puedes ingresar una nueva.', 'success')
        return render_template("backend/pln-day.html",success=True)
    
@blueprintname.route(f'/report-test/')
@traceError
@login_required
def reportTest():
    classname = request.args.get("classname")
    if not classname:
        return "No se ha especificado el nombre de la clase"
    fieldQuery = request.args.get("fieldQuery")
    if not fieldQuery:
        return "No se ha especificado el campo de consulta"
    valueFieldQuery = request.args.get("valueFieldQuery")
    if not valueFieldQuery:
        return "No se ha especificado el valor del campo de consulta"
    fieldGroupBy = request.args.get("fieldGroupBy")
    if not fieldGroupBy:
        return "No se ha especificado el campo de agrupación"
    
    query = session.newQuery(classname)
    query.addFilter(fieldQuery, "==", valueFieldQuery)
    table = query.getCountBy("id",fieldGroupBy)

    jsonData = {}
    for item in table:
        jsonData[item[0]] = item[1]
    return jsonData

@blueprintname.route(f'/report-pln/')
@traceError
@login_required
def report_pln():
    query = session.newQuery("SurveyMarchTwo")
    print(query.count())
    
    ### plnCandidate groups
    plnCandidate_groups = ["a. Gilbert Jiménez","b. Carolina Delgado","c. Alvaro Ramos","d. Marvin Taylor","f. NS/NR", "e. Ninguno"]
    query.addFilter("plnScale", "or",["8","9","10"])
    total = query.count()
    print(total)
    response = {}
    for i, item in enumerate(plnCandidate_groups):
        query = session.newQuery("SurveyMarchTwo")
        query.addFilter("plnScale", "or",["8","9","10"])
        query.addFilter("plnCandidate","==",item)
        abs = query.count()
        porc = round((float(abs) / float(total) * 100.0), 2)
        data = {}
        data["absolutos"] = abs
        data["porcentajes"] = porc
        response[item] = data

    return response

@blueprintname.route(f'/import/')
@traceError
@login_required
def importclazz():
    from utils.methods.stats import import_clazz
    from dictfields import dict_fields
    import_clazz(dict_fields)
    return "Importado correctamente"

@blueprintname.route(f'/report/<int:record_id>/')
@traceError
@login_required
def report(record_id):
    from utils.methods.stats import generateReport
    classname = application.get_class_name(record_id)
    stats = generateReport(classname,record_id)
    params = False
    if record_id == 1:
        return render_template("backend/stats-febrero.html",stats=stats)
    elif record_id == 2:
        return render_template("backend/stats-marzo.html",stats=stats)
    elif record_id == 3:
        #return stats
        return render_template("backend/stats-marzo-dos.html",stats=stats)
    elif record_id == 4:
        now = engine.now().strftime("%Y-%m-%d %H:%M:%S")
        #return stats
        return render_template("backend/stats-mayo.html",stats=stats,last_loaded_time=now)
    elif record_id == 5:
        #return stats
        return render_template("backend/stats-may.html",stats=stats)
    elif record_id == 6:
        #return stats
        return render_template("backend/stats-mayo-dos.html",stats=stats)
    elif record_id == 7:
        params = {
            "userCreation":"Encuestador",
            "gender":"Género",
            "age":"Edad",
            "conoceCarlos":"Conoce usted a Carlos Hidalgo?",
            "opinionCarlos":"¿Cuál es su opinión sobre Carlos Hidalgo?",
            "conoceRodrigoChaves":"Conoce usted a Rodrigo Chaves?",
            "opinionRodrigoChaves":"¿Cuál es su opinión sobre Rodrigo Chaves?",
            "apoyaAlcalde":"¿Apoya usted la gestión del alcalde, Carlos Hidalgo?",
            "muniScale":"Del 1 al 10 como califica la labor de la Municipalidad de Turrialba?.",
            "apoyaRodrigoChaves":"¿Apoya usted la gestión del presidente Rodrigo Chaves?",
            "chavesParty":"¿Apoyaría usted un partido impulsado por el presidente, Rodrigo Chaves? ",
            "contact":"Contacto"
            }
    elif record_id == 15:
        params = {
            "userCreation":"Encuestador",
            "gender":"Género",
            "age":"Edad",
            "county":"Distrito",
            "party":"Partido",
            "chavesSupport":"Apoya usted la gestión del presidente Rodrigo Chaves?",
            "nationalElection":"Si las elecciones nacionales fueran hoy, ¿por quién votaría?",
            "aguilarConoce":"Conoce usted a José Aguilar Berrocal?",
            "aguilarOpinion":"Opinión sobre José Aguilar Berrocal",
            "arielConoce":"Conoce usted a Ariel Robles?",
            "arielOpinion":"Opinión sobre Ariel Robles",
            "apoyaAlcalde":"Apoya usted la gestión del actual alcalde de su cantón?",
            "contact":"Contacto"
            }
        county = request.args.get("county")
        #return stats
        return render_template("backend/stats.html",stats=stats,params=params,county=county)

