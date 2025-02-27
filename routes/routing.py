
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

@blueprintname.route(f'/survey/', methods=["GET","POST"])
@traceError
@login_required
def survey():
    class_names = application.list_class_names()
    classname = application.get_class_name(1)
    classnameLabel = application.get_class_name_label(1)
    containers = get_clazz_fields(1)

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
    
@blueprintname.route(f'/report-by-user/')
@traceError
@login_required
def reportbyuser():
    stats = session.getVariable("stats")
    return render_template("backend/statsbyuser.html",stats=stats)

@blueprintname.route(f'/report/')
@traceError
@login_required
def report():
    from utils.methods.stats import field_count, countbygender
    ### Age groups
    age_groups = [
    "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
    "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
    "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
    "m. + 80"
    ]
    age = countbygender("age",age_groups)

    ### gender groups
    masc = field_count("gender", "A. Masculino")
    fem = field_count("gender", "B. Femenino")
    tot = masc + fem
    gender = {
            "Hombres":masc,
            "Mujeres":fem,
            "Total":tot
    }

    ### State groups
    state_groups = ["1. San José","2. Alajuela","3. Cartago","4. Heredia","5. Guanacaste","6. Puntarenas","7. Limón"]
    state = countbygender("state",state_groups)
    
    ### User groups
    userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]
    userCreation = countbygender("createdby_id",userCreation_groups)

    ### party groups
    party_groups = ["a. Partido Liberación Nacional","b. Partido Unidad Social Cristiana","c. Partido Nueva República","d. Partido Progreso Social Democrático","e. Frente Amplio","f. Partido Liberal Progresista","g. PAC","h. PNG","i. Pueblo Soberano","j. Unidos Podemos","k. Otro","l. Ninguno","m. NS/NR"]
    party = countbygender("party",party_groups)

    ### PartyAndChaves groups
    partyandchaves_groups = ["a. Partido Liberación Nacional","b. Partido Unidad Social Cristiana","c. Partido Nueva República","d. Partido Progreso Social Democrático","e. Frente Amplio","f. Partido Liberal Progresista","g. PAC","h. PNG","i. Pueblo Soberano","j. Unidos Podemos","k. Partido de Chaves","l. Otro","m. Ninguno","n. NS/NR"]
    partyAndChaves = countbygender("partyAndChaves",partyandchaves_groups)

    ### Conoce Chaves groups
    conoceRodrigoChaves_groups = ["a. Sí","b. No","c. NS/NR"]
    conoceRodrigoChaves = countbygender("conoceRodrigoChaves",conoceRodrigoChaves_groups)

    ### Opinión Chaves groups
    opinionRodrigoChaves_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
    opinionRodrigoChaves = countbygender("opinionRodrigoChaves",opinionRodrigoChaves_groups)

    ### Conoce conoceMauricioBatalla groups
    conoceMauricioBatalla_groups = ["a. Sí","b. No","c. NS/NR"]
    conoceMauricioBatalla = countbygender("conoceMauricioBatalla",conoceMauricioBatalla_groups)

    ### Opinión opinionMauricioBatalla groups
    opinionMauricioBatalla_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
    opinionMauricioBatalla = countbygender("opinionMauricioBatalla",opinionMauricioBatalla_groups)

    ### Conoce conoceLauraFernandez groups
    conoceLauraFernandez_groups = ["a. Sí","b. No","c. NS/NR"]
    conoceLauraFernandez = countbygender("conoceLauraFernandez",conoceLauraFernandez_groups)

    ### Opinión opinionLauraFernandez groups
    opinionLauraFernandez_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
    opinionLauraFernandez = countbygender("opinionLauraFernandez",opinionLauraFernandez_groups)

    ### Conoce conoceAlvaroRamos groups
    conoceAlvaroRamos_groups = ["a. Sí","b. No","c. NS/NR"]
    conoceAlvaroRamos = countbygender("conoceAlvaroRamos",conoceAlvaroRamos_groups)

    ### Opinión opinionAlvaroRamos groups
    opinionAlvaroRamos_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
    opinionAlvaroRamos = countbygender("opinionAlvaroRamos",opinionAlvaroRamos_groups)

    ### Conoce conoceGilbertJimenez groups
    conoceGilbertJimenez_groups = ["a. Sí","b. No","c. NS/NR"]
    conoceGilbertJimenez = countbygender("conoceGilbertJimenez",conoceGilbertJimenez_groups)

    ### Opinión opinionGilbertJimenez groups
    opinionGilbertJimenez_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
    opinionGilbertJimenez = countbygender("opinionGilbertJimenez",opinionGilbertJimenez_groups)

    ### Conoce conoceCarolinaDelgado groups
    conoceCarolinaDelgado_groups = ["a. Sí","b. No","c. NS/NR"]
    conoceCarolinaDelgado = countbygender("conoceCarolinaDelgado",conoceCarolinaDelgado_groups)

    ### Opinión opinionCarolinaDelgado groups
    opinionCarolinaDelgado_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
    opinionCarolinaDelgado = countbygender("opinionCarolinaDelgado",opinionCarolinaDelgado_groups)

    ### Conoce conoceMarvinTaylor groups
    conoceMarvinTaylor_groups = ["a. Sí","b. No","c. NS/NR"]
    conoceMarvinTaylor = countbygender("conoceMarvinTaylor",conoceMarvinTaylor_groups)

    ### Opinión opinionMarvinTaylor groups
    opinionMarvinTaylor_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
    opinionMarvinTaylor = countbygender("opinionMarvinTaylor",opinionMarvinTaylor_groups)

    ### Conoce conoceRolandoArayaMonge groups
    conoceRolandoArayaMonge_groups = ["a. Sí","b. No","c. NS/NR"]
    conoceRolandoArayaMonge = countbygender("conoceRolandoArayaMonge",conoceRolandoArayaMonge_groups)

    ### Opinión opinionRolandoArayaMonge groups
    opinionRolandoArayaMonge_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
    opinionRolandoArayaMonge = countbygender("opinionRolandoArayaMonge",opinionRolandoArayaMonge_groups)

    ############ Apoyos Políticos ############

    ### Partido Presidente
    chavesParty_groups = ["a. Sí","b. No","c. NS/NR"]
    chavesParty = countbygender("chavesParty",chavesParty_groups)

    ### chavesCandidate groups
    chavesCandidate_groups = ["a. Mauricio Batalla","b. Laura Fernandez","c. Otro","d. NS/NR"]
    chavesCandidate = countbygender("chavesCandidate",chavesCandidate_groups)
    
    ### plnElections
    plnElections_groups = ["a. Sí","b. No","c. NS/NR"]
    plnElections = countbygender("plnElections",plnElections_groups)

    ### plnCandidate groups
    plnCandidate_groups = ["a. Gilbert Jiménez","b. Carolina Delgado","c. Alvaro Ramos","d. Marvin Taylor","e. NS/NR"]
    plnCandidate = countbygender("plnCandidate",plnCandidate_groups)

    ### generalElections
    generalElections_groups = ["Mauricio Batalla","Laura Fernandez","Álvaro Ramos","Fabricio Alvarado","Eliécer Feinzaig","Gilbert Jiménez","Carolina Delgado","Claudia Dobles","Sofia Guillen","Juan Carlos Hidalgo","Rolando Araya Monge","Luis Amador","Marvin Taylor","Natalia Diaz","Claudio Alpizar","Fernando Zamora","Ninguno","NS/NR"]
    generalElections = countbygender("generalElections",generalElections_groups)

    ### chavesSupport
    chavesSupport_groups = ["a. Sí","b. No","c. NS/NR"]
    chavesSupport = countbygender("chavesSupport",chavesSupport_groups)

    ### chavesScale
    chavesScale_groups = ["1","2","3","4","5","6","7","8","9","10"]
    chavesScale = countbygender("chavesScale",chavesScale_groups)

    stats = {
        "age":age,
        "gender":gender,
        "state":state,
        "party":party,
        "partyAndChaves":partyAndChaves,
        "conoceRodrigoChaves":conoceRodrigoChaves,
        "opinionRodrigoChaves":opinionRodrigoChaves,
        "conoceMauricioBatalla":conoceMauricioBatalla,
        "opinionMauricioBatalla":opinionMauricioBatalla,
        "conoceLauraFernandez":conoceLauraFernandez,
        "opinionLauraFernandez":opinionLauraFernandez,
        "conoceAlvaroRamos":conoceAlvaroRamos,
        "opinionAlvaroRamos":opinionAlvaroRamos,
        "conoceGilbertJimenez":conoceGilbertJimenez,
        "opinionGilbertJimenez":opinionGilbertJimenez,
        "conoceCarolinaDelgado":conoceCarolinaDelgado,
        "opinionCarolinaDelgado":opinionCarolinaDelgado,
        "conoceMarvinTaylor":conoceMarvinTaylor,
        "opinionMarvinTaylor":opinionMarvinTaylor,
        "conoceRolandoArayaMonge":conoceRolandoArayaMonge,
        "opinionRolandoArayaMonge":opinionRolandoArayaMonge,
        "chavesParty":chavesParty,
        "chavesCandidate":chavesCandidate,
        "plnElections":plnElections,
        "plnCandidate":plnCandidate,
        "generalElections":generalElections,
        "chavesSupport":chavesSupport,
        "chavesScale":chavesScale,
        "userCreation":userCreation
    }
    session.putVariable("stats",stats)
    return stats
    #return render_template("backend/stats.html",stats=stats)
