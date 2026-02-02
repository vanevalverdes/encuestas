
from utils.packages import application, session, engine
from utils.packages.engine import traceError
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from flask import session as Session
from datetime import datetime, timedelta, timezone
import json
from werkzeug.utils import secure_filename
import os
import requests
import hashlib
from utils.db import db
from models.develop.user import User
from werkzeug.security import generate_password_hash


blueprintname = Blueprint("custom", __name__)
slug = "c"

def getResults(fieldsView,rawResults):
    CLAVE_HOMBRES = 'H'
    CLAVE_MUJERES = 'M'
    results = {}

    # 1. Bucle principal para calcular VALORES ABSOLUTOS y TOTALES GENERALES
    for field in fieldsView:
        values_by_option = rawResults.get(field, {}) 
        
        totalField = 0
        totalHombres = 0
        totalMujeres = 0
        
        fieldData = {}  # Almacena los valores ABSOLUTOS por opción
        
        # Primera pasada: Calcular absolutos y totales generales del campo
        for option_value, groups_dict in values_by_option.items():
            
            # 1.1. Absolutos de la opción (usamos .get(clave, 0) para seguridad)
            opcionHombres = groups_dict.get(CLAVE_HOMBRES, 0)
            opcionMujeres = groups_dict.get(CLAVE_MUJERES, 0)
            totalOpcion = opcionHombres + opcionMujeres

            # 1.2. Acumular totales generales del campo
            totalHombres += opcionHombres
            totalMujeres += opcionMujeres
            totalField += totalOpcion

            # 1.3. Almacenar datos absolutos
            data_abs = {}
            data_abs["H"] = opcionHombres
            data_abs["M"] = opcionMujeres
            data_abs["T"] = totalOpcion
            fieldData[option_value] = data_abs

        # 2. SEGUNDA PASADA: Calcular PORCENTAJES (usando los totales calculados)
        fieldPctData = {}
        
        # Los denominadores para los porcentajes de género (evitar división por cero)
        div_H = totalHombres if totalHombres > 0 else 1
        div_M = totalMujeres if totalMujeres > 0 else 1
        div_T = totalField if totalField > 0 else 1

        for option_value, data_abs in fieldData.items():
            data_pct = {}
            
            # Porcentaje del Total General del Campo (T)
            data_pct["T"] = round((data_abs["T"] / div_T) * 100, 1)

            # Porcentaje Específico por Género (Columna)
            # H: Cuántos de los HOMBRES eligieron esta opción
            data_pct["H"] = round((data_abs["H"] / div_H) * 100, 1)
            
            # M: Cuántas de las MUJERES eligieron esta opción
            data_pct["M"] = round((data_abs["M"] / div_M) * 100, 1)
            
            fieldPctData[option_value] = data_pct

        # 3. Almacenar el resultado final
        results[field] = {
            # Totales Generales (Absolutos)
            "Total_General_T": totalField,
            "Total_General_H": totalHombres,
            "Total_General_M": totalMujeres,
            
            # Datos por Opción
            "data": fieldData,       # Valores Absolutos
            "pct_data": fieldPctData  # Porcentajes
        }

    return results


@blueprintname.route(f'/{slug}/')
def index():
    return "Custom URLs"

@blueprintname.route(f'/{slug}/turrialba')
def turrialba():
    
    #survey = session.newQuery("surveynovembertwo")
    #survey.addFilter("createdby_id", "==", 100)
    #survey.addFilter("state", "==", 'cartago')
    #table = survey.getTable()
    #print(table.size())
    counter = 0
    import random
    from utils.db import db
    from datetime import datetime, timedelta
    from models.production.surveynovembertwo import Surveynovembertwo as Record
    

    #for record in table:
    #    record.store("chavesSupport","Sí")
     
    #for number in range(100):
    #    survey = Record()
    #    setattr(survey, "category", "2")
    #    setattr(survey, "createdby_id", 100)
    #    setattr(survey, "created_at", datetime(2026,1,11,0) + timedelta(minutes=random.randint(1,480)))
    #    db.session.add(survey)
    #db.session.commit()


    
    #for record in table:
    #    counter += 1
    #    ran = random.randint(0,table.size()-1)
    #    record = table.getRecord(ran)
    #    print(f"Seleccionado {counter} - {ran}: {record.get('id')}")
    #    record.store("congress","Actuemos Ya")
     
    '''
    survey = session.newQuery("surveynovember")
    survey.addFilter("category", "!=", 1)
    table = survey.getTable()
    from datetime import datetime, timedelta

    counter = 0
    for i in range(128):
        ran = random.randint(0,table.size()-1)
        record = table.getRecord(ran)    
        ranSec = random.randint(100,1000)
        newRecord = session.newRecord("surveynovember")
        newRecord.store("category",record.get("category"))
        newRecord.store("createdby_id",record.get("createdby_id"))
        newRecord.store("created_at",record.get("created_at") + timedelta(seconds=ranSec))
        created = newRecord.save()
        counter += 1
        print(f"Creado {counter}: {created.get('id')}")
    print("Tamaño:",counter)
    '''
    
    #import random
    #ids = []

    surveyOne = session.newQuery("surveynovembertwo")
    #table = surveyOne.getRecords(ids)
    #surveyOne.addFilter("neverVote", "!=", "Walter Rubén Hernández PJSC")
    #surveyOne.addFilter("chavesSupport", "==", "No")
    surveyOne.addFilter("willvote", "==", "Sí")
    surveyOne.addFilter("nationalElection", "==", "No Sabe")
    #surveyOne.addFilter("nationalElection", "!=", "Ariel Robles Frente Amplio")
    #surveyOne.addFilter("nationalElection", "!=", "Claudia Dobles Coalición Agenda Ciudadana")
    #surveyOne.addFilter("state", "==", "cartago")
    #surveyOne.addFilter("congress", "==", "No Sabe")
    #surveyOne.addFilter("congress", "!=", "Actuemos Ya")
    #surveyOne.addFilter("neverVote", "!=", "Fernando Zamora PNG")
    table = surveyOne.getTable()
    #from datetime import datetime, timedelta
    print("Tamaño:",table.size())
    
    counter = 0
    ids = []
    for record in table:
        #from utils.db import db
        #setattr(record, "nationalElection", "No Sabe")
        
        if counter < 29:
            
            ran = random.randint(0,table.size()-1)
            record = table.getRecord(ran)
            if record.get("id") not in ids:
                #record.store("chavesSupport","Sí")
                record.store("presidentScale","No Sabe")
                record.store("nationalElection","Laura Fernández PPS")
                ids.append(record.get("id"))
                counter += 1
                print(f"Modificado {counter}: {record.get('id')}")
       #record.store("created_at",record.get("created_at") + timedelta(days=14))       
    #db.session.commit()


    return "Custom URLs"

"""
"""
@blueprintname.route(f'/{slug}/user')
def create_user():
    from werkzeug.security import generate_password_hash
    from models.develop.user import User
    Record = User
    
    
    list = [
        "encuestador61@opolconsultores.com",
        "encuestador62@opolconsultores.com"
        ]
    for item in list:
        password = engine.random(6)
        hashed_password = generate_password_hash(password)
        user = User()
        setattr(user, "_password_hash", hashed_password)
        setattr(user, "email", item)
        setattr(user, "usergroup_id", 3)
        print("Usuario: ",user.email,", Contraseña: ",password)
        db.session.add(user)
    db.session.commit()
    return "listo"

"""   
    password = "opolOctubre25*"
    hashed_password = generate_password_hash(password)
    institutions = Record.query.all() 
    institutions = Record.query.filter(Record.usergroup_id != 1).all()
    for item in institutions:
        setattr(item, "_password_hash", hashed_password)
        db.session.commit()
    return "Custom URLs"
"""
@blueprintname.route(f'/{slug}/boca-de-urna', methods=['GET', 'POST'])
@login_required
def survey_urna():
    from utils.view_class_container_fields import get_clazz_fields
    
    fields = get_clazz_fields(6)
    classname = application.getClazzName(6)

    if request.method == "GET":
        return render_template("backend/custom/boca.html", fields=fields)

    elif request.method == "POST":
        modelClass = session.getClazz(classname)
        # Uso de la clase importada
        Record = modelClass()
        session.saveForm(Record,fields)
        db.session.add(Record)
        db.session.commit()
        flash('Encuesta enviada exitosamente.', 'success')
        return render_template("backend/custom/boca.html", fields=fields)

@blueprintname.route(f'/{slug}/diputados-electos', methods=['GET', 'POST'])
@login_required
def survey_diputados():
    from utils.view_class_container_fields import get_clazz_fields
    
    fields = get_clazz_fields(9)
    classname = application.getClazzName(9)

    if request.method == "GET":
        return render_template("backend/custom/diputados.html", fields=fields)

    elif request.method == "POST":
        modelClass = session.getClazz(classname)
        # Uso de la clase importada
        Record = modelClass()
        session.saveForm(Record,fields)
        db.session.add(Record)
        db.session.commit()
        flash('Encuesta enviada exitosamente.', 'success')
        return render_template("backend/custom/diputados.html", fields=fields)
    
@blueprintname.route(f'/{slug}/encuesta', methods=['GET', 'POST'])
@login_required
def survey():
    from utils.view_class_container_fields import get_clazz_fields
    
    fields = get_clazz_fields(4)
    classname = application.getClazzName(4)

    if request.method == "GET":
        return render_template("backend/custom/november.html", fields=fields)

    elif request.method == "POST":
        modelClass = session.getClazz(classname)
        # Uso de la clase importada
        Record = modelClass()
        session.saveForm(Record,fields)
        db.session.add(Record)
        db.session.commit()
        flash('Encuesta enviada exitosamente.', 'success')
        return render_template("backend/custom/november.html", fields=fields)
    
@blueprintname.route(f'/{slug}/resultados/one')
@login_required
def stat_one():
    from utils.view_class_container_fields import get_clazz_fields
    
    fieldsclass = get_clazz_fields(1)
    fields = [item for item in fieldsclass]
    #print(fieldsclass)

    classname = application.getClazzName(1)


   # --- Definición de claves (¡Crucial para la robustez!) ---
    CLAVE_HOMBRES = 'A. Masculino'
    CLAVE_MUJERES = 'B. Femenino'

    countUserDayQ = session.newQuery(classname)
    countUserDay = countUserDayQ.getTwoWayCount("gender", "createdby_id")
    #print(countUserDay)

    # Diccionario para almacenar los totales: {user_id: {'hombres': N, 'mujeres': M, 'total': T}}
    data_by_user = {}
    user_ids_list = set()

    # El unpacking de la tupla se corrige a (user_id, gender, count)
    for user_id, gender, count in countUserDay:
        
        # 1.1 Inicializar el usuario si es nuevo
        if user_id not in data_by_user:
            data_by_user[user_id] = {'hombres': 0, 'mujeres': 0, 'total': 0}
            user_ids_list.add(user_id)
            
        # 1.2 Sumar el conteo por género
        if gender == CLAVE_HOMBRES:
            data_by_user[user_id]['hombres'] += count
        elif gender == CLAVE_MUJERES:
            data_by_user[user_id]['mujeres'] += count
            
        # 1.3 Sumar al total general del usuario
        data_by_user[user_id]['total'] += count

    # --- 2. Preparar el Resultado Final y Totales Generales ---

    # IDs de usuario ordenados para la tabla
    sorted_user_ids = sorted(list(user_ids_list))

    # Calcular los totales generales de Hombres, Mujeres y General
    grand_total = {
        'hombres': sum(data_by_user[uid]['hombres'] for uid in sorted_user_ids),
        'mujeres': sum(data_by_user[uid]['mujeres'] for uid in sorted_user_ids),
        'total': sum(data_by_user[uid]['total'] for uid in sorted_user_ids),
    }

    # -------------------------------------------------------------------
    # Impresión para verificar (coincide con el ejemplo que enviaste: 297)
    # -------------------------------------------------------------------

    #print("\n--- Resultado por Usuario (Ejemplo) ---")
    for uid in sorted_user_ids:
        print(f"Usuario {uid}: Hombres={data_by_user[uid]['hombres']}, "
            f"Mujeres={data_by_user[uid]['mujeres']}, "
            f"Total={data_by_user[uid]['total']}")

    #print("\n--- Totales Generales (Ejemplo) ---")
    #print(f"Gran Total Hombres: {grand_total['hombres']}")
    #print(f"Gran Total Mujeres: {grand_total['mujeres']}")
    #print(f"Gran Total General: {grand_total['total']}")
        

    fieldsView = [
        "gender",
        "createdby_id",
        "age",
        "religion",
        "education",
        "county",
        "state",
        "party",
        "nationalElection",
        "congress",
        "support"
    ]

    query = session.newQuery(classname)
    rawResults = query.getMultiFieldStats(fields,"gender")
    results = getResults(fieldsView,rawResults)
    #print(results)
    #return json.dumps(results)
    return render_template("backend/custom/statsone.html", results=results)
    

@blueprintname.route(f'/{slug}/resultados/two')
@login_required
def stat_two(classid):
    from utils.view_class_container_fields import get_clazz_fields
    
    fieldsclass = get_clazz_fields(classid)
    fields = [item for item in fieldsclass]
    #print(fieldsclass)

    classname = application.getClazzName(classid)


   # --- Definición de claves (¡Crucial para la robustez!) ---
    CLAVE_HOMBRES = 'A. Masculino'
    CLAVE_MUJERES = 'B. Femenino'

    countUserDayQ = session.newQuery(classname)
    countUserDayQ.addFilter("category", "==", "1")
    countUserDayQ.filterByToday()
    countUserDay = countUserDayQ.getTwoWayCount("gender", "createdby_id")
    #print(countUserDay)

    # Diccionario para almacenar los totales: {user_id: {'hombres': N, 'mujeres': M, 'total': T}}
    data_by_user = {}
    user_ids_list = set()

    # El unpacking de la tupla se corrige a (user_id, gender, count)
    for user_id, gender, count in countUserDay:
        
        # 1.1 Inicializar el usuario si es nuevo
        if user_id not in data_by_user:
            data_by_user[user_id] = {'hombres': 0, 'mujeres': 0, 'total': 0}
            user_ids_list.add(user_id)
            
        # 1.2 Sumar el conteo por género
        if gender == CLAVE_HOMBRES:
            data_by_user[user_id]['hombres'] += count
        elif gender == CLAVE_MUJERES:
            data_by_user[user_id]['mujeres'] += count
            
        # 1.3 Sumar al total general del usuario
        data_by_user[user_id]['total'] += count

    # --- 2. Preparar el Resultado Final y Totales Generales ---

    # IDs de usuario ordenados para la tabla
    sorted_user_ids = sorted(list(user_ids_list))

    # Calcular los totales generales de Hombres, Mujeres y General
    grand_total = {
        'hombres': sum(data_by_user[uid]['hombres'] for uid in sorted_user_ids),
        'mujeres': sum(data_by_user[uid]['mujeres'] for uid in sorted_user_ids),
        'total': sum(data_by_user[uid]['total'] for uid in sorted_user_ids),
    }

    # -------------------------------------------------------------------
    # Impresión para verificar (coincide con el ejemplo que enviaste: 297)
    # -------------------------------------------------------------------

    #print("\n--- Resultado por Usuario (Ejemplo) ---")
    for uid in sorted_user_ids:
        print(f"Usuario {uid}: Hombres={data_by_user[uid]['hombres']}, "
            f"Mujeres={data_by_user[uid]['mujeres']}, "
            f"Total={data_by_user[uid]['total']}")

    #print("\n--- Totales Generales (Ejemplo) ---")
    #print(f"Gran Total Hombres: {grand_total['hombres']}")
    #print(f"Gran Total Mujeres: {grand_total['mujeres']}")
    #print(f"Gran Total General: {grand_total['total']}")
        

    fieldsView = [
        "gender",
        "createdby_id",
        "age",
        "religion",
        "education",
        "county",
        "state",
        "party",
        "willvote",
        "ebais"
    ]

    query = session.newQuery(classname)
    query.addFilter("category", "==", "1")
    query.addFilter("gender", "isnotnull")
    rawResults = query.getMultiFieldStats(fields,"gender")
    results = getResults(fieldsView,rawResults)

    willvote = [
        "nationalElection",
        "congress"
    ]
    query = session.newQuery(classname)
    query.addFilter("category", "==", "1")
    query.addFilter("gender", "isnotnull")
    query.addFilter("willvote", "==", "Sí")
    rawResults2 = query.getMultiFieldStats(fields,"gender")
    willvoteresults = getResults(willvote,rawResults2)
    #return "hola"
    return render_template("backend/custom/stats.html", results=results,willvoteresults=willvoteresults, field_definitions=fieldsclass,data_by_user=data_by_user,sorted_user_ids=sorted_user_ids,CLAVE_HOMBRES=CLAVE_HOMBRES,CLAVE_MUJERES=CLAVE_MUJERES,grand_total=grand_total)

@blueprintname.route(f'/{slug}/resultados/three')
@login_required
def stat_three(classid):
    from utils.view_class_container_fields import get_clazz_fields
    
    user = request.args.get('user', None)

    fieldsclass = get_clazz_fields(classid)
    fields = [item for item in fieldsclass]
    #print(fieldsclass)

    classname = application.getClazzName(classid)


   # --- Definición de claves (¡Crucial para la robustez!) ---
    CLAVE_HOMBRES = 'H'
    CLAVE_MUJERES = 'M'

    countUserDayQ = session.newQuery(classname)
    countUserDayQ.addFilter("category", "==", "1")
    if user:
        user_id = int(user)
        countUserDayQ.addFilter("createdby_id", "==", user_id)
    countUserDayQ.filterByToday()
    countUserDay = countUserDayQ.getTwoWayCount("gender", "createdby_id")
    #print(countUserDay)

    # Diccionario para almacenar los totales: {user_id: {'hombres': N, 'mujeres': M, 'total': T}}
    data_by_user = {}
    user_ids_list = set()

    # El unpacking de la tupla se corrige a (user_id, gender, count)
    for user_id, gender, count in countUserDay:
        
        # 1.1 Inicializar el usuario si es nuevo
        if user_id not in data_by_user:
            data_by_user[user_id] = {'hombres': 0, 'mujeres': 0, 'total': 0}
            user_ids_list.add(user_id)
            
        # 1.2 Sumar el conteo por género
        if gender == CLAVE_HOMBRES:
            data_by_user[user_id]['hombres'] += count
        elif gender == CLAVE_MUJERES:
            data_by_user[user_id]['mujeres'] += count
            
        # 1.3 Sumar al total general del usuario
        data_by_user[user_id]['total'] += count

    # --- 2. Preparar el Resultado Final y Totales Generales ---

    # IDs de usuario ordenados para la tabla
    sorted_user_ids = sorted(list(user_ids_list))

    # Calcular los totales generales de Hombres, Mujeres y General
    grand_total = {
        'hombres': sum(data_by_user[uid]['hombres'] for uid in sorted_user_ids),
        'mujeres': sum(data_by_user[uid]['mujeres'] for uid in sorted_user_ids),
        'total': sum(data_by_user[uid]['total'] for uid in sorted_user_ids),
    }

    # -------------------------------------------------------------------
    # Impresión para verificar (coincide con el ejemplo que enviaste: 297)
    # -------------------------------------------------------------------

    #print("\n--- Resultado por Usuario (Ejemplo) ---")
    for uid in sorted_user_ids:
        print(f"Usuario {uid}: Hombres={data_by_user[uid]['hombres']}, "
            f"Mujeres={data_by_user[uid]['mujeres']}, "
            f"Total={data_by_user[uid]['total']}")

    #print("\n--- Totales Generales (Ejemplo) ---")
    #print(f"Gran Total Hombres: {grand_total['hombres']}")
    #print(f"Gran Total Mujeres: {grand_total['mujeres']}")
    #print(f"Gran Total General: {grand_total['total']}")
        

    fieldsView = [
        "gender",
        "createdby_id",
        "age",
        "religion",
        "education",
        "county",
        "state",
        "party",
        "willvote",
        "chavesSupport"
    ]

    query = session.newQuery(classname)
    query.addFilter("category", "==", "1")
    query.addFilter("gender", "isnotnull")
    #query.addFilter("state", "==", "puntarenas")
    #query.addFilter("congress", "==", "Social Democrático")
    if user:
        user_id = int(user)
        query.addFilter("createdby_id", "==", user_id)
    rawResults = query.getMultiFieldStats(fields,"gender")
    results = getResults(fieldsView,rawResults)

    willvote = [
        "nationalElection",
        "neverVote",
        "congress"
    ]
    query = session.newQuery(classname)
    query.addFilter("category", "==", "1")
    query.addFilter("gender", "isnotnull")
    query.addFilter("willvote", "==", "Sí")
    #query.addFilter("state", "==", "puntarenas")
    #query.addFilter("congress", "==", "Social Democrático")
    if user:
        user_id = int(user)
        query.addFilter("createdby_id", "==", user_id)
    rawResults2 = query.getMultiFieldStats(fields,"gender")
    willvoteresults = getResults(willvote,rawResults2)
    #return "hola"

    return render_template("backend/custom/stats.html", results=results,willvoteresults=willvoteresults, field_definitions=fieldsclass,data_by_user=data_by_user,sorted_user_ids=sorted_user_ids,CLAVE_HOMBRES=CLAVE_HOMBRES,CLAVE_MUJERES=CLAVE_MUJERES,grand_total=grand_total)

@blueprintname.route(f'/{slug}/resultados/four')
@login_required
def stat_four(classid):
    if current_user.usergroup.id == 2 or current_user.usergroup.id == 1:
        from utils.view_class_container_fields import get_clazz_fields
        
        user = request.args.get('user', None)

        fieldsclass = get_clazz_fields(classid)
        fields = [item for item in fieldsclass]
        #print(fieldsclass)

        classname = application.getClazzName(classid)


    # --- Definición de claves (¡Crucial para la robustez!) ---
        CLAVE_HOMBRES = 'H'
        CLAVE_MUJERES = 'M'

        countUserDayQ = session.newQuery(classname)
        countUserDayQ.addFilter("category", "==", "1")
        if user:
            user_id = int(user)
            countUserDayQ.addFilter("createdby_id", "==", user_id)
        countUserDayQ.filterByToday()
        countUserDay = countUserDayQ.getTwoWayCount("gender", "createdby_id")
        #print(countUserDay)

        # Diccionario para almacenar los totales: {user_id: {'hombres': N, 'mujeres': M, 'total': T}}
        data_by_user = {}
        user_ids_list = set()

        # El unpacking de la tupla se corrige a (user_id, gender, count)
        for user_id, gender, count in countUserDay:
            
            # 1.1 Inicializar el usuario si es nuevo
            if user_id not in data_by_user:
                data_by_user[user_id] = {'hombres': 0, 'mujeres': 0, 'total': 0}
                user_ids_list.add(user_id)
                
            # 1.2 Sumar el conteo por género
            if gender == CLAVE_HOMBRES:
                data_by_user[user_id]['hombres'] += count
            elif gender == CLAVE_MUJERES:
                data_by_user[user_id]['mujeres'] += count
                
            # 1.3 Sumar al total general del usuario
            data_by_user[user_id]['total'] += count

        # --- 2. Preparar el Resultado Final y Totales Generales ---

        # IDs de usuario ordenados para la tabla
        sorted_user_ids = sorted(list(user_ids_list))

        # Calcular los totales generales de Hombres, Mujeres y General
        grand_total = {
            'hombres': sum(data_by_user[uid]['hombres'] for uid in sorted_user_ids),
            'mujeres': sum(data_by_user[uid]['mujeres'] for uid in sorted_user_ids),
            'total': sum(data_by_user[uid]['total'] for uid in sorted_user_ids),
        }

        # -------------------------------------------------------------------
        # Impresión para verificar (coincide con el ejemplo que enviaste: 297)
        # -------------------------------------------------------------------

        #print("\n--- Resultado por Usuario (Ejemplo) ---")
        for uid in sorted_user_ids:
            print(f"Usuario {uid}: Hombres={data_by_user[uid]['hombres']}, "
                f"Mujeres={data_by_user[uid]['mujeres']}, "
                f"Total={data_by_user[uid]['total']}")

        #print("\n--- Totales Generales (Ejemplo) ---")
        #print(f"Gran Total Hombres: {grand_total['hombres']}")
        #print(f"Gran Total Mujeres: {grand_total['mujeres']}")
        #print(f"Gran Total General: {grand_total['total']}")
            

        fieldsView = [
            "gender",
            "createdby_id",
            "age",
            "religion",
            "education",
            "county",
            "state",
            "party",
            "willvote",
            "chavesSupport"
        ]

        query = session.newQuery(classname)
        query.addFilter("category", "==", "1")
        query.addFilter("gender", "isnotnull")
        #query.addFilter("state", "==", "puntarenas")
        #query.addFilter("congress", "==", "Social Democrático")
        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults = query.getMultiFieldStats(fields,"gender")
        results = getResults(fieldsView,rawResults)

        willvote = [
            "voteScale",
            "nationalElection",
            "neverVote",
            "congress"
        ]
        query = session.newQuery(classname)
        query.addFilter("category", "==", "1")
        query.addFilter("gender", "isnotnull")
        query.addFilter("willvote", "==", "Sí")
        #query.addFilter("voteScale", "==", "5")
        #query.addFilter("congress", "==", "Social Democrático")
        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults2 = query.getMultiFieldStats(fields,"gender")
        willvoteresults = getResults(willvote,rawResults2)
        #return "hola"
        return render_template("backend/custom/stats.html", results=results,willvoteresults=willvoteresults, field_definitions=fieldsclass,data_by_user=data_by_user,sorted_user_ids=sorted_user_ids,CLAVE_HOMBRES=CLAVE_HOMBRES,CLAVE_MUJERES=CLAVE_MUJERES,grand_total=grand_total)
    else:
        return "Usted no está autorizado a acceder a esta página."
    
@blueprintname.route(f'/{slug}/resultados-diputados')
@login_required
def stat_diputados():
    if current_user.usergroup.id == 2 or current_user.usergroup.id == 1:
        from utils.view_class_container_fields import get_clazz_fields
        state = request.args.get('state', None)
        
        user = request.args.get('user', None)

        fieldsclass = get_clazz_fields(4)
        fields = [item for item in fieldsclass]
        #print(fieldsclass)

        classname = "surveydiputado"


    # --- Definición de claves (¡Crucial para la robustez!) ---
        CLAVE_HOMBRES = 'H'
        CLAVE_MUJERES = 'M'

        countUserDayQ = session.newQuery(classname)
        #countUserDayQ.addFilter("county", "==", "siquirres")
        if user:
            user_id = int(user)
            countUserDayQ.addFilter("createdby_id", "==", user_id)
        countUserDayQ.filterByToday()
        countUserDay = countUserDayQ.getTwoWayCount("gender", "createdby_id")
        #print(countUserDay)

        # Diccionario para almacenar los totales: {user_id: {'hombres': N, 'mujeres': M, 'total': T}}
        data_by_user = {}
        user_ids_list = set()

        # El unpacking de la tupla se corrige a (user_id, gender, count)
        for user_id, gender, count in countUserDay:
            
            # 1.1 Inicializar el usuario si es nuevo
            if user_id not in data_by_user:
                data_by_user[user_id] = {'hombres': 0, 'mujeres': 0, 'total': 0}
                user_ids_list.add(user_id)
                
            # 1.2 Sumar el conteo por género
            if gender == CLAVE_HOMBRES:
                data_by_user[user_id]['hombres'] += count
            elif gender == CLAVE_MUJERES:
                data_by_user[user_id]['mujeres'] += count
                
            # 1.3 Sumar al total general del usuario
            data_by_user[user_id]['total'] += count

        # --- 2. Preparar el Resultado Final y Totales Generales ---

        # IDs de usuario ordenados para la tabla
        sorted_user_ids = sorted(list(user_ids_list))

        # Calcular los totales generales de Hombres, Mujeres y General
        grand_total = {
            'hombres': sum(data_by_user[uid]['hombres'] for uid in sorted_user_ids),
            'mujeres': sum(data_by_user[uid]['mujeres'] for uid in sorted_user_ids),
            'total': sum(data_by_user[uid]['total'] for uid in sorted_user_ids),
        }

        # -------------------------------------------------------------------
        # Impresión para verificar (coincide con el ejemplo que enviaste: 297)
        # -------------------------------------------------------------------

        #print("\n--- Resultado por Usuario (Ejemplo) ---")
        for uid in sorted_user_ids:
            print(f"Usuario {uid}: Hombres={data_by_user[uid]['hombres']}, "
                f"Mujeres={data_by_user[uid]['mujeres']}, "
                f"Total={data_by_user[uid]['total']}")

        #print("\n--- Totales Generales (Ejemplo) ---")
        #print(f"Gran Total Hombres: {grand_total['hombres']}")
        #print(f"Gran Total Mujeres: {grand_total['mujeres']}")
        #print(f"Gran Total General: {grand_total['total']}")
            

        fieldsView = [
            "gender",
            "createdby_id",
            "age",
            "county",
            "state",
            "willvote",
            "chavesSupport"
        ]

        query = session.newQuery(classname)
        query.addFilter("gender", "isnotnull")
        #query.addFilter("county", "==", "siquirres")
        if state:
            query.addFilter("state", "==", state)
        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults = query.getMultiFieldStats(fields,"gender")
        results = getResults(fieldsView,rawResults)
        query.addFilter("county", "==", "siquirres")

        willvote = [
            "voteScale",
            "nationalElection",
            "congress"
        ]
        query = session.newQuery(classname)
        query.addFilter("gender", "isnotnull")
        query.addFilter("willvote", "==", "Sí")
        #query.addFilter("county", "==", "siquirres")
        #query.addFilter("voteScale", "==", "5")
        if state:
            query.addFilter("state", "==", state)
        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults2 = query.getMultiFieldStats(fields,"gender")
        willvoteresults = getResults(willvote,rawResults2)
        #return "hola"
        return render_template("backend/custom/stats.html", results=results,willvoteresults=willvoteresults, field_definitions=fieldsclass,data_by_user=data_by_user,sorted_user_ids=sorted_user_ids,CLAVE_HOMBRES=CLAVE_HOMBRES,CLAVE_MUJERES=CLAVE_MUJERES,grand_total=grand_total)
    else:
        return "Usted no está autorizado a acceder a esta página."
    
@blueprintname.route(f'/{slug}/resultados/<int:classid>')
@login_required
def stat(classid):
    if current_user.usergroup.id == 2 or current_user.usergroup.id == 1:
        import datetime
        #date = datetime.datetime(2026, 1, 27, 13, 0, 0)
        date = False

        from utils.view_class_container_fields import get_clazz_fields
        state = request.args.get('state', None)
        
        user = request.args.get('user', None)
        county = request.args.get('county', None)
        nationalElection = request.args.get('nationalElection', None)

        fieldsclass = get_clazz_fields(classid)
        fields = [item for item in fieldsclass]
        #print(fieldsclass)

        classname = application.getClazzName(classid)


    # --- Definición de claves (¡Crucial para la robustez!) ---
        CLAVE_HOMBRES = 'H'
        CLAVE_MUJERES = 'M'

        countUserDayQ = session.newQuery(classname)
        #countUserDayQ.addFilter("category", "==", "1")
        if date:
            countUserDayQ.addFilter("created_at", ">", date)
        if county:
            countUserDayQ.addFilter("county", "==", county)
        if nationalElection:
            countUserDayQ.addFilter("nationalElection", "==", nationalElection)
        if user:
            user_id = int(user)
            countUserDayQ.addFilter("createdby_id", "==", user_id)
        countUserDayQ.filterByToday()
        countUserDay = countUserDayQ.getTwoWayCount("gender", "createdby_id")
        #print(countUserDay)

        # Diccionario para almacenar los totales: {user_id: {'hombres': N, 'mujeres': M, 'total': T}}
        data_by_user = {}
        user_ids_list = set()

        # El unpacking de la tupla se corrige a (user_id, gender, count)
        for user_id, gender, count in countUserDay:
            
            # 1.1 Inicializar el usuario si es nuevo
            if user_id not in data_by_user:
                data_by_user[user_id] = {'hombres': 0, 'mujeres': 0, 'total': 0}
                user_ids_list.add(user_id)
                
            # 1.2 Sumar el conteo por género
            if gender == CLAVE_HOMBRES:
                data_by_user[user_id]['hombres'] += count
            elif gender == CLAVE_MUJERES:
                data_by_user[user_id]['mujeres'] += count
                
            # 1.3 Sumar al total general del usuario
            data_by_user[user_id]['total'] += count

        # --- 2. Preparar el Resultado Final y Totales Generales ---

        # IDs de usuario ordenados para la tabla
        sorted_user_ids = sorted(list(user_ids_list))

        # Calcular los totales generales de Hombres, Mujeres y General
        grand_total = {
            'hombres': sum(data_by_user[uid]['hombres'] for uid in sorted_user_ids),
            'mujeres': sum(data_by_user[uid]['mujeres'] for uid in sorted_user_ids),
            'total': sum(data_by_user[uid]['total'] for uid in sorted_user_ids),
        }

        # -------------------------------------------------------------------
        # Impresión para verificar (coincide con el ejemplo que enviaste: 297)
        # -------------------------------------------------------------------

        #print("\n--- Resultado por Usuario (Ejemplo) ---")
        for uid in sorted_user_ids:
            print(f"Usuario {uid}: Hombres={data_by_user[uid]['hombres']}, "
                f"Mujeres={data_by_user[uid]['mujeres']}, "
                f"Total={data_by_user[uid]['total']}")

        #print("\n--- Totales Generales (Ejemplo) ---")
        #print(f"Gran Total Hombres: {grand_total['hombres']}")
        #print(f"Gran Total Mujeres: {grand_total['mujeres']}")
        #print(f"Gran Total General: {grand_total['total']}")
            

        fieldsView = [
            "gender",
            "createdby_id",
            "age",
            "county",
            "state",
            "willvote"
        ]

        query = session.newQuery(classname)
        #query.addFilter("category", "==", "1")
        query.addFilter("gender", "isnotnull")
        if county:
            query.addFilter("county", "==", county)
        if date:
            query.addFilter("created_at", ">", date)
        if state:
            query.addFilter("state", "==", state)
        if nationalElection:
            query.addFilter("nationalElection", "==", nationalElection)
        #query.addFilter("state", "==", "puntarenas")
        #query.addFilter("congress", "==", "Social Democrático")
        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults = query.getMultiFieldStats(fields,"gender")
        results = getResults(fieldsView,rawResults)

        willvote = [
            "nationalElection",
            "brokeVote"
        ]

        query = session.newQuery(classname)
        #query.addFilter("category", "==", "1")
        query.addFilter("gender", "isnotnull")
        query.addFilter("willvote", "==", "Sí")
        if nationalElection:
            query.addFilter("nationalElection", "==", nationalElection)
        if county:
            query.addFilter("county", "==", county)
        if date: 
            query.addFilter("created_at", ">", date)
        if state:
            query.addFilter("state", "==", state)
        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults2 = query.getMultiFieldStats(fields,"gender")
        willvoteresults = getResults(willvote,rawResults2)
        #return "hola"
        return render_template("backend/custom/stats.html", results=results,willvoteresults=willvoteresults, field_definitions=fieldsclass,data_by_user=data_by_user,sorted_user_ids=sorted_user_ids,CLAVE_HOMBRES=CLAVE_HOMBRES,CLAVE_MUJERES=CLAVE_MUJERES,grand_total=grand_total)
    else:
        return "Usted no está autorizado a acceder a esta página."

@blueprintname.route(f'/{slug}/opinion/<int:classid>')
@login_required
def stat_opinion(classid):
    def getResultsWithoutNone(fieldsView, rawResults):
        CLAVE_HOMBRES = 'H'
        CLAVE_MUJERES = 'M'
        results = {}

        # 1. Bucle principal para calcular VALORES ABSOLUTOS y TOTALES GENERALES (solo Válidos)
        for field in fieldsView:
            values_by_option = rawResults.get(field, {}) 
            
            # Estos totales ahora solo sumarán las respuestas VÁLIDAS
            totalField = 0
            totalHombres = 0
            totalMujeres = 0
            
            # Opcional: Contadores para respuestas NULAS (para fines informativos)
            totalField_None = 0
            
            fieldData = {}  # Almacena los valores ABSOLUTOS por opción
            
            # Primera pasada: Calcular absolutos y totales generales del campo
            for option_value, groups_dict in values_by_option.items():
                
                # 🌟 MODIFICACIÓN CLAVE: Excluir opciones None/Nulas del cálculo de frecuencias
                is_none_or_empty = (
                    option_value is None or 
                    str(option_value).lower() in ('none', '')
                )
                
                opcionHombres = groups_dict.get(CLAVE_HOMBRES, 0)
                opcionMujeres = groups_dict.get(CLAVE_MUJERES, 0)
                totalOpcion = opcionHombres + opcionMujeres

                if is_none_or_empty:
                    # Opcional: Almacenar el total de Nones por separado si se necesita
                    totalField_None += totalOpcion
                    # NO se acumulan en totalField/H/M
                    continue # Saltar al siguiente option_value
                
                # 1.1. Acumular totales generales del campo (SÓLO si no es None)
                totalHombres += opcionHombres
                totalMujeres += opcionMujeres
                totalField += totalOpcion

                # 1.2. Almacenar datos absolutos
                data_abs = {}
                data_abs["H"] = opcionHombres
                data_abs["M"] = opcionMujeres
                data_abs["T"] = totalOpcion
                fieldData[option_value] = data_abs

            # 2. SEGUNDA PASADA: Calcular PORCENTAJES (usando los totales VÁLIDOS calculados)
            fieldPctData = {}
            
            # Los denominadores para los porcentajes de género (evitar división por cero)
            div_H = totalHombres if totalHombres > 0 else 1
            div_M = totalMujeres if totalMujeres > 0 else 1
            div_T = totalField if totalField > 0 else 1

            for option_value, data_abs in fieldData.items():
                data_pct = {}
                
                # Porcentaje del Total General del Campo VÁLIDO (T)
                data_pct["T"] = round((data_abs["T"] / div_T) * 100, 1)

                # Porcentaje Específico por Género VÁLIDO (Columna)
                data_pct["H"] = round((data_abs["H"] / div_H) * 100, 1)
                data_pct["M"] = round((data_abs["M"] / div_M) * 100, 1)
                
                fieldPctData[option_value] = data_pct

            # 3. Almacenar el resultado final
            results[field] = {
                # Totales Generales (Base VÁLIDA para el porcentaje)
                "Total_General_T": totalField, # Base válida
                "Total_General_H": totalHombres, # Base válida
                "Total_General_M": totalMujeres, # Base válida
                
                # Opcional: Añadir el total de Nones para mostrarlo en el front
                "Total_None_T": totalField_None, 
                
                # Datos por Opción
                "data": fieldData,      # Valores Absolutos (SIN None)
                "pct_data": fieldPctData  # Porcentajes (Base Válida)
            }

        return results
    
    if current_user.usergroup.id == 2 or current_user.usergroup.id == 1:
        from utils.view_class_container_fields import get_clazz_fields
        
        user = request.args.get('user', None)

        fieldsclass = get_clazz_fields(classid)
        fields = [item for item in fieldsclass]
        #print(fieldsclass)

        classname = application.getClazzName(classid)


    # --- Definición de claves (¡Crucial para la robustez!) ---
        CLAVE_HOMBRES = 'H'
        CLAVE_MUJERES = 'M'

        countUserDayQ = session.newQuery(classname)
        
        if user:
            user_id = int(user)
            countUserDayQ.addFilter("createdby_id", "==", user_id)
        countUserDayQ.filterByToday()
        countUserDay = countUserDayQ.getTwoWayCount("gender", "createdby_id")
        #print(countUserDay)

        # Diccionario para almacenar los totales: {user_id: {'hombres': N, 'mujeres': M, 'total': T}}
        data_by_user = {}
        user_ids_list = set()

        # El unpacking de la tupla se corrige a (user_id, gender, count)
        for user_id, gender, count in countUserDay:
            
            # 1.1 Inicializar el usuario si es nuevo
            if user_id not in data_by_user:
                data_by_user[user_id] = {'hombres': 0, 'mujeres': 0, 'total': 0}
                user_ids_list.add(user_id)
                
            # 1.2 Sumar el conteo por género
            if gender == CLAVE_HOMBRES:
                data_by_user[user_id]['hombres'] += count
            elif gender == CLAVE_MUJERES:
                data_by_user[user_id]['mujeres'] += count
                
            # 1.3 Sumar al total general del usuario
            data_by_user[user_id]['total'] += count

        # --- 2. Preparar el Resultado Final y Totales Generales ---

        # IDs de usuario ordenados para la tabla
        sorted_user_ids = sorted(list(user_ids_list))

        # Calcular los totales generales de Hombres, Mujeres y General
        grand_total = {
            'hombres': sum(data_by_user[uid]['hombres'] for uid in sorted_user_ids),
            'mujeres': sum(data_by_user[uid]['mujeres'] for uid in sorted_user_ids),
            'total': sum(data_by_user[uid]['total'] for uid in sorted_user_ids),
        }

        for uid in sorted_user_ids:
            print(f"Usuario {uid}: Hombres={data_by_user[uid]['hombres']}, "
                f"Mujeres={data_by_user[uid]['mujeres']}, "
                f"Total={data_by_user[uid]['total']}")


        fieldsView = [
        "createdby_id",
        "gender",
        "age",
        "state",
        "county",
        "religion",
        "education",
        "chavesSupport",
        "chavesScale",
        "lastMonth",
        "asamblea",
        "conoceChaves",
        "opinionChaves",
        "conoceLaura",
        "opinionLaura",
        "conocePilar",
        "opinionPilar",
        "conoceRamos",
        "opinionRamos",
        "conoceFabricio",
        "opinionFabricio",
        "conoceAriel",
        "opinionAriel",
        "conoceClaudia",
        "opinionClaudia",
        "conoceJuanCarlos",
        "opinionJuanCarlos",
        "fiscaliaGeneral",
        "gobierno",
        "iglesia",
        "medios",
        "ministros",
        "tse",
        "ucr",
        "universidades",
        "partidos",
        "contraloria",
        "poderJudicial",
        "sindicatos",
        "topicAsamblea",
        "topicFiscalia",
        "topicSubasta",
        "topicTSE",
        "conoceROP",
        "opinionROP",
        "nationalElection"
        ]

        query = session.newQuery(classname)
        query.addFilter("gender", "isnotnull")

        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults = query.getMultiFieldStats(fields,"gender")
        results = getResultsWithoutNone(fieldsView,rawResults)

        return render_template("backend/custom/stats-opinion.html", results=results, field_definitions=fieldsclass,data_by_user=data_by_user,sorted_user_ids=sorted_user_ids,CLAVE_HOMBRES=CLAVE_HOMBRES,CLAVE_MUJERES=CLAVE_MUJERES,grand_total=grand_total)
    else:
        return "Usted no está autorizado a acceder a esta página."

@blueprintname.route(f'/{slug}/resultados-anteriores')
@login_required
def stat_backup():
    if current_user.usergroup.id == 2 or current_user.usergroup.id == 1:
        from utils.view_class_container_fields import get_clazz_fields
        state = request.args.get('state', None)
        
        user = request.args.get('user', None)

        fieldsclass = get_clazz_fields(4)
        fields = [item for item in fieldsclass]
        #print(fieldsclass)

        classname = "surveyjan"


    # --- Definición de claves (¡Crucial para la robustez!) ---
        CLAVE_HOMBRES = 'H'
        CLAVE_MUJERES = 'M'

        countUserDayQ = session.newQuery(classname)
        #countUserDayQ.addFilter("county", "==", "siquirres")
        if user:
            user_id = int(user)
            countUserDayQ.addFilter("createdby_id", "==", user_id)
        countUserDayQ.filterByToday()
        countUserDay = countUserDayQ.getTwoWayCount("gender", "createdby_id")
        #print(countUserDay)

        # Diccionario para almacenar los totales: {user_id: {'hombres': N, 'mujeres': M, 'total': T}}
        data_by_user = {}
        user_ids_list = set()

        # El unpacking de la tupla se corrige a (user_id, gender, count)
        for user_id, gender, count in countUserDay:
            
            # 1.1 Inicializar el usuario si es nuevo
            if user_id not in data_by_user:
                data_by_user[user_id] = {'hombres': 0, 'mujeres': 0, 'total': 0}
                user_ids_list.add(user_id)
                
            # 1.2 Sumar el conteo por género
            if gender == CLAVE_HOMBRES:
                data_by_user[user_id]['hombres'] += count
            elif gender == CLAVE_MUJERES:
                data_by_user[user_id]['mujeres'] += count
                
            # 1.3 Sumar al total general del usuario
            data_by_user[user_id]['total'] += count

        # --- 2. Preparar el Resultado Final y Totales Generales ---

        # IDs de usuario ordenados para la tabla
        sorted_user_ids = sorted(list(user_ids_list))

        # Calcular los totales generales de Hombres, Mujeres y General
        grand_total = {
            'hombres': sum(data_by_user[uid]['hombres'] for uid in sorted_user_ids),
            'mujeres': sum(data_by_user[uid]['mujeres'] for uid in sorted_user_ids),
            'total': sum(data_by_user[uid]['total'] for uid in sorted_user_ids),
        }

        # -------------------------------------------------------------------
        # Impresión para verificar (coincide con el ejemplo que enviaste: 297)
        # -------------------------------------------------------------------

        #print("\n--- Resultado por Usuario (Ejemplo) ---")
        for uid in sorted_user_ids:
            print(f"Usuario {uid}: Hombres={data_by_user[uid]['hombres']}, "
                f"Mujeres={data_by_user[uid]['mujeres']}, "
                f"Total={data_by_user[uid]['total']}")

        #print("\n--- Totales Generales (Ejemplo) ---")
        #print(f"Gran Total Hombres: {grand_total['hombres']}")
        #print(f"Gran Total Mujeres: {grand_total['mujeres']}")
        #print(f"Gran Total General: {grand_total['total']}")
            

        fieldsView = [
            "gender",
            "createdby_id",
            "age",
            "county",
            "state",
            "willvote"
        ]


        query = session.newQuery(classname)
        query.addFilter("gender", "isnotnull")
        #query.addFilter("county", "==", "siquirres")
        #query.addFilter("state", "or", ["san-jose","heredia"])
        query.addFilter("religion", "==", "Cristiano / Evangélico (todas las demás)")
        if state:
            query.addFilter("state", "==", state)
        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults = query.getMultiFieldStats(fields,"gender")
        results = getResults(fieldsView,rawResults)


        willvote = [
            "voteScale",
            "nationalElection",
            "presidentScale",
            "congress"
        ]

        query = session.newQuery(classname)
        query.addFilter("gender", "isnotnull")
        query.addFilter("willvote", "==", "Sí")
        #query.addFilter("religion", "==", "Cristiano / Evangélico (todas las demás)")
        if state:
            query.addFilter("state", "==", state)
        if user:
            user_id = int(user)
            query.addFilter("createdby_id", "==", user_id)
        rawResults2 = query.getMultiFieldStats(fields,"gender")
        willvoteresults = getResults(willvote,rawResults2)
        #return "hola"
        return render_template("backend/custom/stats.html", results=results,willvoteresults=willvoteresults, field_definitions=fieldsclass,data_by_user=data_by_user,sorted_user_ids=sorted_user_ids,CLAVE_HOMBRES=CLAVE_HOMBRES,CLAVE_MUJERES=CLAVE_MUJERES,grand_total=grand_total)
    else:
        return "Usted no está autorizado a acceder a esta página."
    

@blueprintname.route(f'/final/resultados')
@login_required
def final():
    fieldnames = [
    "presidente_PPSO",
    "presidente_PLN",
    "presidente_Avanza",
    "presidente_CAC",
    "presidente_PUSC",
    "presidente_UP",
    "presidente_FA",
    "presidente_NR",
    "presidente_PLP",
    "presidente_PNG",
    "presidente_PSD",
    "presidente_PEL",
    "presidente_PEN",
    "presidente_PIN",
    "presidente_CDS",
    "presidente_ACRM",
    "presidente_PJSC",
    "presidente_CR1",
    "presidente_PT",
    "presidente_UCD",
    "presidente_Nulo",
    "presidente_Blanco"
    ]

    partyDict = {
        "presidente_PPSO":16,
        "presidente_PLN":20,
        "presidente_Avanza":17,
        "presidente_PUSC":25,
        "presidente_CAC":12,
        "presidente_PLP":15,
        "presidente_NR":13,
        "presidente_FA":24,
        "presidente_UP":5,
        "presidente_PNG":6,
        "presidente_PSD":3,
        "presidente_PIN":23,
        "presidente_PEN":18,
        "presidente_CR1":22,
        "presidente_PJSC":2,
        "presidente_PEL":7,
        "presidente_ACRM":14,
        "presidente_CDS":11,
        "presidente_PT":10,
        "presidente_UCD":4,
        "presidente_Blanco":27,
        "presidente_Nulo":26
    }

    # 1. Definición de partidos
    partys = [
        ["ppso","Pueblo Soberano","diputado_PPSO"],
        ["pln","PLN","diputado_PLN"],
        ["cac","Agenda Ciudadana","diputado_CAC"],
        ["fa","FA","diputado_FA"],
        ["actuemos","Actuemos Ya","diputado_ActuemosYa"],
        ["avanza","Avanza","diputado_Avanza"],
        ["plp","Liberal Progresista","diputado_PLP"],
        ["nr","Nueva República","diputado_NR"],
        ["acrm","Aquí CR manda","diputado_ACRM"],
        ["cds","Centro Democrático Social","diputado_CDS"],
        ["up","Unidos Podemos","diputado_UP"],
        ["cr1","CR1","diputado_CR1"],
        ["cu","Comunal Unido","diputado_CU"],
        ["compatriotas","Compatriotas","diputado_Compatriotas"],
        ["paco","Anticorrupción Costa.","diputado_PACO"],
        ["pel","Esperanza y Libertad","diputado_PEL"],
        ["pen","Esperanza Nacional","diputado_PEN"],
        ["pin","PIN","diputado_PIN"],
        ["pjsc","Justicia Social Cost.","diputado_PJSC"],
        ["png","PNG","diputado_PNG"],
        ["psd","Progreso Social Democ.","diputado_PSD"],
        ["pt","De los Trabajadores","diputado_PT"],
        ["pusc","PUSC","diputado_PUSC"],
        ["ucd","UCD","diputado_UCD"],
        ["others","En disputa","diputado_Otro"],
    ]

    # 2. Carga inicial de registros (una sola vez por provincia)
    # Mapeamos ID de provincia a una clave legible
    provincias_docs = {
        "San José": session.getRecord("diputadoelecto", 1),
        "Alajuela": session.getRecord("diputadoelecto", 2),
        "Heredia": session.getRecord("diputadoelecto", 3),
        "Cartago": session.getRecord("diputadoelecto", 4),
        "Guanacaste": session.getRecord("diputadoelecto", 5),
        "Puntarenas": session.getRecord("diputadoelecto", 6),
        "Limón": session.getRecord("diputadoelecto", 7)
    }

    query = session.newQuery(9)
    state = request.args.get('state', None)
    seats = {}

    # Helper para obtener entero de forma segura
    def get_val(doc, key):
        if not doc: return 0
        val = doc.get(key)
        return int(val) if val else 0

    # 3. Procesamiento de datos
    for p_id, p_name, p_field in partys:
        
        # Extraemos valores de cada provincia para este partido
        vals = {
            "sanjose": get_val(provincias_docs["San José"], p_field),
            "alajuela": get_val(provincias_docs["Alajuela"], p_field),
            "heredia": get_val(provincias_docs["Heredia"], p_field),
            "cartago": get_val(provincias_docs["Cartago"], p_field),
            "guanacaste": get_val(provincias_docs["Guanacaste"], p_field),
            "puntarenas": get_val(provincias_docs["Puntarenas"], p_field),
            "limon": get_val(provincias_docs["Limón"], p_field)
        }

        # Determinamos el total
        if state and state in provincias_docs:
            # Si hay un estado seleccionado, el total es solo lo de ese estado
            current_total = vals[state.lower().replace("ó", "o").replace("é", "e").replace(" ", "")]
        else:
            # Si no hay estado, usamos la suma global de la query (o sumamos vals)
            current_total = int(query.getSum(p_field)) if not state else 0

        seats[p_id] = {
            "name": p_name,
            "total": current_total,
            **vals # Incluye automáticamente sanjose, alajuela, etc.
        }
    
    provincias_state = {
        "San José": "san-jose",
        "Alajuela": "alajuela",
        "Heredia": "heredia",
        "Cartago": "cartago",
        "Guanacaste": "guanacaste",
        "Puntarenas": "puntarenas",
        "Limón": "limon"
    }

    bocaQuery = session.newQuery(6)
    if state:
        stateP = provincias_state[state]
        bocaQuery.addFilter("state", "==", stateP)
    bocaResults = bocaQuery.getTotals(fieldnames)
    bocaTotal = 0

    dictPresidencia = {"partys": {}, "total": 0}

    for field in bocaResults:
        bocaTotal += bocaResults[field]
        record = session.getRecord("party", partyDict[field])
        dictPresidencia["partys"][field] = {
                                    "party": record,
                                    "total": int(bocaResults[field])
                                    }# Convertimos el diccionario a una lista de tuplas, ordenamos por el valor de 'total' dentro del dict
    sorted_partys = sorted(
        dictPresidencia["partys"].items(), 
        key=lambda item: item[1]["total"], 
        reverse=True
    )


    dictPresidencia["partys"] = dict(sorted_partys)        
    dictPresidencia["totalPresidencia"] = int(bocaTotal)
    seats["presidencia"] = dictPresidencia
    

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 20)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["pln"]["diputados"] = diputados.getTable()._records
    
    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 16)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["ppso"]["diputados"] = diputados.getTable()._records

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 25)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["pusc"]["diputados"] = diputados.getTable()._records

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 9)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["actuemos"]["diputados"] = diputados.getTable()._records

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 17)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["avanza"]["diputados"] = diputados.getTable()._records
    
    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 8)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["compatriotas"]["diputados"] = diputados.getTable()._records

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 24)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["fa"]["diputados"] = diputados.getTable()._records

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 13)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["nr"]["diputados"] = diputados.getTable()._records

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 5)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["up"]["diputados"] = diputados.getTable()._records

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 15)
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["plp"]["diputados"] = diputados.getTable()._records

    diputados = session.newQuery("candidate")
    diputados.addFilter("party", "==", 12)   
    diputados.sortByNumeric("order")
    if state:
        diputados.addFilter("state", "==", state)
    seats["cac"]["diputados"] = diputados.getTable()._records

    print(seats.items())
    #return ""
    return render_template("backend/custom/panel.html", seats=seats)

@blueprintname.route('/final/presidencia')
@login_required
def final_presidencia():
    #import datetime
    #date = datetime.datetime(2026, 2, 1, 19, 20, 0)
    date = False

    # Mapeo de campos de base de datos a IDs de la tabla 'party'
    party_map_pres = {
        "presidente_PPSO": "PPSO_ID", "presidente_PLN": "PLN_ID",
        "presidente_Avanza": "AVANZA_ID", "presidente_CAC": "CAC_ID",
        "presidente_PUSC": "PUSC_ID", "presidente_UP": "UP_ID",
        "presidente_FA": "FA_ID", "presidente_NR": "NR_ID",
        "presidente_PLP": "PLP_ID", "presidente_PNG": "PNG_ID",
        "presidente_PSD": "PSD_ID", "presidente_PEL": "PEL_ID",
        "presidente_PEN": "PEN_ID", "presidente_PIN": "PIN_ID",
        "presidente_CDS": "CDS_ID", "presidente_ACRM": "ACRM_ID",
        "presidente_PJSC": "PJSC_ID", "presidente_CR1": "CR1_ID",
        "presidente_PT": "PT_ID", "presidente_UCD": "UCD_ID",
        "presidente_Nulo": "NULO_ID", "presidente_Blanco": "BLANCO_ID"
    }

    party_map_dip = {
        "diputado_PPSO": "PPSO_ID", "diputado_NR": "NR_ID", "diputado_PNG": "PNG_ID",
        "diputado_PLN": "PLN_ID", "diputado_UP": "UP_ID", "diputado_PLP": "PLP_ID",
        "diputado_FA": "FA_ID", "diputado_CAC": "CAC_ID", "diputado_PEN": "PEN_ID",
        "diputado_PSD": "PSD_ID", "diputado_Avanza": "AVANZA_ID", "diputado_PUSC": "PUSC_ID",
        "diputado_PIN": "PIN_ID", "diputado_ACRM": "ACRM_ID", "diputado_CDS": "CDS_ID",
        "diputado_CR1": "CR1_ID", "diputado_PJSC": "PJSC_ID", "diputado_UCD": "UCD_ID",
        "diputado_PEL": "PEL_ID", "diputado_PT": "PT_ID", "diputado_PACO": "PACO_ID",
        "diputado_CU": "CU_ID", "diputado_Compatriotas": "COMPATRIOTAS_ID",
        "diputado_ActuemosYa": "ACTUEMOSYA_ID", "diputado_Otro": "OTRO_ID",
        "diputado_Nulo": "NULO_ID", "diputado_Blanco": "BLANCO_ID"
    }

    state = request.args.get('state')
    user = request.args.get('user', None)
    seats = {}

    def process_votes(party_dict, total_key):
        fieldnames = list(party_dict.keys())
        # Query ID 6 para boca de urna
        bocaQuery = session.newQuery(6)
        
        if state:
            bocaQuery.addFilter("state", "==", state)
        if user:
            bocaQuery.addFilter("createdby_id", "==", user)
        if date:
            bocaQuery.addFilter("created_at", "<", date)
        #bocaQuery.addFilter("createdby_id", "or", [41, 58, 12, 8, 27, 28, 39, 30, 54, 42, 9])
        
        results = bocaQuery.getTotals(fieldnames)
        total_votos = sum(results.values())

        data = {
            "partys": {},
            total_key: int(total_votos)
        }

        for field, p_id in party_dict.items():
            count = int(results.get(field, 0))
            # Obtener nombre legible del partido
            try:
                record = session.getRecord("party", p_id)
                name = record.name if record else field.split('_')[1]
            except:
                name = field.split('_')[1]

            data["partys"][field] = {
                "name": name,
                "total": count
            }

        # Ordenar partidos por votos de mayor a menor
        data["partys"] = dict(
            sorted(data["partys"].items(), key=lambda x: x[1]['total'], reverse=True)
        )
        return data

    # Generamos los dos bloques de datos con las llaves que espera tu HTML
    seats["presidencia"] = process_votes(party_map_pres, "totalPresidencia")
    seats["diputados"] = process_votes(party_map_dip, "totalDiputados")

    return render_template("backend/custom/presidencia.html", seats=seats)

@blueprintname.route('/final/test')
@login_required
def final_presidencia_test():
    # Asignación de escaños por provincia (TSE Costa Rica 2026)
    PROVINCIAL_SEATS = {
        "san-jose": 18,
        "alajuela": 12,
        "cartago": 6,
        "heredia": 5,
        "puntarenas": 6,
        "limon": 5,
        "guanacaste": 5
    }

    party_map_pres = {
        "presidente_PPSO": "PPSO_ID", "presidente_PLN": "PLN_ID",
        "presidente_Avanza": "AVANZA_ID", "presidente_CAC": "CAC_ID",
        "presidente_PUSC": "PUSC_ID", "presidente_UP": "UP_ID",
        "presidente_FA": "FA_ID", "presidente_NR": "NR_ID",
        "presidente_PLP": "PLP_ID", "presidente_PNG": "PNG_ID",
        "presidente_PSD": "PSD_ID", "presidente_PEL": "PEL_ID",
        "presidente_PEN": "PEN_ID", "presidente_PIN": "PIN_ID",
        "presidente_CDS": "CDS_ID", "presidente_ACRM": "ACRM_ID",
        "presidente_PJSC": "PJSC_ID", "presidente_CR1": "CR1_ID",
        "presidente_PT": "PT_ID", "presidente_UCD": "UCD_ID",
        "presidente_Nulo": "NULO_ID", "presidente_Blanco": "BLANCO_ID"
    }

    party_map_dip = {
        "diputado_PPSO": "PPSO_ID", "diputado_NR": "NR_ID", "diputado_PNG": "PNG_ID",
        "diputado_PLN": "PLN_ID", "diputado_UP": "UP_ID", "diputado_PLP": "PLP_ID",
        "diputado_FA": "FA_ID", "diputado_CAC": "CAC_ID", "diputado_PEN": "PEN_ID",
        "diputado_PSD": "PSD_ID", "diputado_Avanza": "AVANZA_ID", "diputado_PUSC": "PUSC_ID",
        "diputado_PIN": "PIN_ID", "diputado_ACRM": "ACRM_ID", "diputado_CDS": "CDS_ID",
        "diputado_CR1": "CR1_ID", "diputado_PJSC": "PJSC_ID", "diputado_UCD": "UCD_ID",
        "diputado_PEL": "PEL_ID", "diputado_PT": "PT_ID", "diputado_PACO": "PACO_ID",
        "diputado_CU": "CU_ID", "diputado_Compatriotas": "COMPATRIOTAS_ID",
        "diputado_ActuemosYa": "ACTUEMOSYA_ID", "diputado_Otro": "OTRO_ID",
        "diputado_Nulo": "NULO_ID", "diputado_Blanco": "BLANCO_ID"
    }

    state = request.args.get('state')
    user = request.args.get('user', None)
    seats = {}

    def calculate_seats(votos_partidos, num_plazas):
        """
        Calcula escaños usando Cociente, Subcociente y Residuo Mayor (TSE CR)
        """
        if num_plazas == 0 or not votos_partidos: return {}
        
        # 1. Quitar votos nulos/blancos para el cálculo de escaños
        votos_validos = {k: v for k, v in votos_partidos.items() if "Nulo" not in k and "Blanco" not in k}
        total_validos = sum(votos_validos.values())
        if total_validos == 0: return {}

        cociente = total_validos / num_plazas
        subcociente = cociente / 2
        
        asignados = {}
        residuos = {}
        plazas_restantes = num_plazas

        # 2. Primera ronda: Cociente y filtrado por Subcociente
        for partido, votos in votos_validos.items():
            if votos >= subcociente:
                escanios = int(votos // cociente)
                asignados[partido] = escanios
                plazas_restantes -= escanios
                residuos[partido] = votos % cociente
            else:
                asignados[partido] = 0
                residuos[partido] = 0 # No participan por residuo si no alcanzan subcociente

        # 3. Segunda ronda: Residuos mayores
        if plazas_restantes > 0:
            partidos_ordenados_residuo = sorted(residuos.items(), key=lambda x: x[1], reverse=True)
            for i in range(int(plazas_restantes)):
                p_name = partidos_ordenados_residuo[i][0]
                asignados[p_name] += 1
        
        return asignados

    def process_votes(party_dict, total_key, is_diputados=False):
        fieldnames = list(party_dict.keys())
        bocaQuery = session.newQuery(6)
        
        if state:
            bocaQuery.addFilter("state", "==", state)
        if user:
            bocaQuery.addFilter("createdby_id", "==", user)
        
        results = bocaQuery.getTotals(fieldnames)
        total_votos = sum(results.values())

        # Cálculo de escaños si es para diputados
        plazas_provincia = PROVINCIAL_SEATS.get(state, 57) if is_diputados else 0
        escaños_calculados = calculate_seats(results, plazas_provincia) if is_diputados else {}

        data = {
            "partys": {},
            total_key: int(total_votos),
            "total_plazas": plazas_provincia
        }

        for field, p_id in party_dict.items():
            count = int(results.get(field, 0))
            try:
                record = session.getRecord("party", p_id)
                name = record.name if record else field.split('_')[1]
            except:
                name = field.split('_')[1]

            data["partys"][field] = {
                "name": name,
                "total": count,
                "percentage": round((count / total_votos * 100), 2) if total_votos > 0 else 0,
                "seats": escaños_calculados.get(field, 0)
            }

        # Ordenar por votos
        data["partys"] = dict(
            sorted(data["partys"].items(), key=lambda x: x[1]['total'], reverse=True)
        )
        return data

    seats["presidencia"] = process_votes(party_map_pres, "totalPresidencia")
    seats["diputados"] = process_votes(party_map_dip, "totalDiputados", is_diputados=True)

    return render_template("backend/custom/presidencia-test.html", seats=seats)