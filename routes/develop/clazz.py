from models.develop.clazz import Clazz, get_fields
from models.develop.container import Container
from utils.generate_class import generate_model_class, ensure_import_exists,clear_file_content
from utils.migrate_class import migrateClass
from utils.methods import application, session, engine
from utils.view_class_container_fields import get_clazz_fields_migration
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from utils.db import db
from werkzeug.utils import secure_filename
from flask_login import login_required
import traceback
from utils.methods.engine import traceError

classname = "clazz"
Record = Clazz

containers = get_fields()
blueprintname = Blueprint("clazz", __name__)

@blueprintname.route(f'/develop/{classname}/new/', methods=["GET","POST"])
@traceError
@login_required
def create_record():
    class_names = application.list_class_names()
    if request.method == "GET":
        return render_template("backend/base/new_base.html", containers=containers,classname=classname, class_names=class_names)
    elif request.method == "POST":

        institution = Record()
        session.saveForm(institution,containers)
        db.session.add(institution)
        db.session.commit()
        return redirect(url_for('.view_record', record_id=institution.id,classname=classname, class_names=class_names))
    
@blueprintname.route(f'/develop/{classname}/<int:record_id>/')
@traceError
@login_required
def view_record(record_id):
    class_names = application.list_class_names()
    institution = application.getClazzDetails(record_id)
    clazz_containers = institution.getContainers()
    clazz_relevants = institution.getRelevants()
    clazz_fields = institution.getFields()
    
    # Consulta para obtener solo los campos `id` y `name`
    #containers_list = db.session.query(Container.id, Container.name).filter_by(clazz_id=record_id).all()

    # Convertir el resultado en una lista de diccionarios (opcional)
    clazz_containers = [{"id": container.id, "name": container.name} for container in clazz_containers]
    # Convertir el resultado en una lista de diccionarios (opcional)
    clazz_relevants = [{"id": relevant.id, "name": repr(relevant)} for relevant in clazz_relevants]
    
    # Convertir el resultado en una lista de diccionarios (opcional)
    clazz_fields = [{"id": relevant.id, "name": repr(relevant)} for relevant in clazz_fields]
    
    #print(containers)
    return render_template('backend/base/view_clazz.html', institution=institution,clazz_fields=clazz_fields, containers=containers,classname=classname, clazz_containers=clazz_containers, clazz_relevants=clazz_relevants, class_names=class_names)

@blueprintname.route(f'/develop/{classname}/<int:record_id>/edit/', methods=['GET', 'POST'])
@traceError
@login_required
def edit_record(record_id):
    class_names = application.list_class_names()
    institution = Record.query.get_or_404(record_id)
    if request.method == 'POST':
        session.saveForm(institution,containers) 
                
        db.session.commit()
        flash('La institución ha sido actualizada exitosamente.', 'success')
        return render_template('backend/base/edit_base.html', institution=institution, containers=containers,classname=classname, class_names=class_names)
    return render_template('backend/base/edit_base.html', institution=institution,containers=containers,classname=classname, class_names=class_names)

@blueprintname.route(f'/develop/{classname}/migrate/', methods=['GET', 'POST'])
@traceError
@login_required
def migrate():
  try:
    def format_classname(name):
        """Formatea un nombre a CamelCase para usarse como nombre de clase."""
        return ''.join(word.capitalize() for word in name.split())

    def format_filename(name):
        """Formatea un nombre a snake_case para usarse como nombre de archivo."""
        return '_'.join(word.lower() for word in name.split())

    table = application.getAllClazzes()

    # Borrar listado en develop
    file_path_statement = 'models/production/clazzlist.py'
    clear_file_content(file_path_statement)
    
    # Borrar listado en produccion
    #file_path_statement = '../production/models/clazzlist.py'
    #clear_file_content(file_path_statement)


    for clazz in table:
        institution = clazz
        fields = get_clazz_fields_migration(clazz.id)
        name = institution.name
        plural = institution.plural
        classname = format_classname(name)
        filename = format_filename(f"{name}.py")
        #print(fields, name, plural, classname,filename)

        # Crea migration en develop
        directory = "models/production"
        response = generate_model_class(fields, classname, filename,directory,plural)
        #print("llega aca")
        
        # Crea migration en production
        #directory = "../production/models/production"
        #response = generate_model_class(fields, classname, filename,directory,plural)
        
        if response:
            import_statement = f'from . import {name.lower()}'
            
            # Crea Class List en Develop
            file_path_statement = 'models/production/clazzlist.py'
            ensure_import_exists(file_path_statement, import_statement)
            
            # Crea Class List en Production
            #file_path_statement = '../production/models/production/clazzlist.py'
            #ensure_import_exists(file_path_statement, import_statement)

            #generate_route_class(record_id,classname,format_filename(name))
            flash(f'{response}', 'success')
        else:
            flash(f'Error', 'danger')
    migrateClass()
    return redirect(url_for(".list_record"))
  except Exception as e:
        print("Error: ", str(e))
        print(traceback.format_exc())
        return str(e), 500

@blueprintname.route(f'/develop/{classname}/<int:record_id>/delete/', methods=['POST'])
@traceError
@login_required
def delete_record(record_id):
    institution = Record.query.get_or_404(record_id)
    db.session.delete(institution)
    db.session.commit()
    flash('La institución ha sido eliminada exitosamente.', 'success')
    return redirect(url_for('.list_record'))  # Asumiendo que existe una ruta para listar instituciones

@blueprintname.route(f'/develop/{classname}/all/')
@traceError
@login_required
def list_record():
    class_names = application.list_class_names()
    institutions = Record.query.all()
    return render_template('backend/base/list_clazz.html', institutions=institutions,classname=classname, class_names=class_names)
