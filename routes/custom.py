
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
    
    #survey = session.newQuery("surveynovember")
    #survey.addFilter("congress", "==", 'No Sabe')
    #survey.addFilter("state", "==", 'cartago')
    #table = survey.getTable()
    #print(table.size())
    #counter = 0
    import random

    #for record in table:
    #    record.store("chavesSupport","Sí")
    # 
    #for number in range(8):
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
    '''
    import random
    countys = [
        "goicoechea",
        "coronado"
    ]
    surveyOne = session.newQuery("surveyoctober")
    print(surveyOne.count())
    surveyOne.addFilter("county", "or", countys)
    table = surveyOne.getTable()
    from datetime import datetime, timedelta
    print(table.getFirstRecord().get('created_at') + timedelta(days=8))
    print("Tamaño:",table.size())

    counter = 0
    for record in table:
        print(record.get("id"))
        newRecord = session.newRecord("surveyoctobertwo")
        newRecord.store("age",record.get("age"))
        newRecord.store("gender",record.get("gender"))
        newRecord.store("religion",record.get("religion"))
        newRecord.store("education",record.get("education"))
        newRecord.store("county",record.get("county"))
        newRecord.store("state",record.get("state"))
        newRecord.store("party",record.get("party"))
        newRecord.store("category","1")
        if record.get("nationalElection") == "Ninguno":
            newRecord.store("willvote","No")
        else:
            newRecord.store("willvote","Sí")
            newRecord.store("nationalElection",record.get("nationalElection"))
            newRecord.store("congress",record.get("congress"))
        newRecord.store("createdby_id",100)
        created = newRecord.save()
        created.store("created_at",record.get("created_at") + timedelta(days=8))
        
        counter += 1
        if counter == 5:
            newRecord = session.newRecord("surveyoctobertwo")
            newRecord.store("category",2)
            newRecord.store("createdby_id",100)
            created = newRecord.save()
            ranSec = random.randint(240,1000)
            created.store("created_at",record.get("created_at") + timedelta(days=9) + timedelta(seconds=ranSec))
            counter = 0
        
    '''


    return "Custom URLs"


@blueprintname.route(f'/{slug}/user')
def create_user():
    from werkzeug.security import generate_password_hash
    from models.develop.user import User
    Record = User
    
    list = [
        "supervisor1@opolconsultores.com",
        "supervisor2@opolconsultores.com",
        "supervisor3@opolconsultores.com",
        "supervisor4@opolconsultores.com",
        "supervisor5@opolconsultores.com"    ]
    password = "octubreOpol*Sup"
    hashed_password = generate_password_hash(password)
    #print(hashed_password)
    for item in list:
        new = Record()
        setattr(new, "name", item)
        setattr(new, "lastname", item)
        setattr(new, "email", item)
        setattr(new, "usergroup_id", 2)
        setattr(new, "_password_hash", hashed_password)
        db.session.add(new)
    db.session.commit()
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
@blueprintname.route(f'/{slug}/encuesta/<int:classid>', methods=['GET', 'POST'])
@login_required
def survey(classid):
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

@blueprintname.route(f'/{slug}/resultados/<int:classid>')
@login_required
def stat(classid):
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
    #query.addFilter("state", "==", "puntarenas")
    #query.addFilter("congress", "==", "Social Democrático")
    if user:
        user_id = int(user)
        query.addFilter("createdby_id", "==", user_id)
    rawResults2 = query.getMultiFieldStats(fields,"gender")
    willvoteresults = getResults(willvote,rawResults2)
    #return "hola"
    return render_template("backend/custom/stats.html", results=results,willvoteresults=willvoteresults, field_definitions=fieldsclass,data_by_user=data_by_user,sorted_user_ids=sorted_user_ids,CLAVE_HOMBRES=CLAVE_HOMBRES,CLAVE_MUJERES=CLAVE_MUJERES,grand_total=grand_total)
