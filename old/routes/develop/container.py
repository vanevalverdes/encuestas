from models.develop.container import Container, get_fields
from utils.methods import application, session
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from utils.db import db
from werkzeug.utils import secure_filename
from flask_login import login_required
import os
from utils.methods.engine import traceError

blueprintname = Blueprint("container", __name__)

classname = "container"
Record = Container
parent = False


@blueprintname.route(f'/develop/{classname}/new/', methods=["GET","POST"])
@traceError
@login_required
def create_record():
    class_names = application.list_class_names()
    parent = request.args.get('parent')
    backlink = request.args.get("backlink")
    print(parent)
    containers = get_fields(parent)
    print(containers)
    
    if request.method == "GET":
        return render_template("backend/base/new_base.html", containers=containers,classname=classname, class_names=class_names,backlink=backlink)
    elif request.method == "POST":

        new_institution = Record()
        session.saveForm(new_institution,containers) 

        db.session.add(new_institution)
        db.session.commit()

        return redirect(url_for('.view_record', record_id=new_institution.id,classname=classname, class_names=class_names,backlink=backlink))
    
@blueprintname.route(f'/develop/{classname}/<int:record_id>')
@traceError
@login_required
def view_record(record_id):
    class_names = application.list_class_names()
    institution = Record.query.get_or_404(record_id)
    backlink = request.args.get("backlink")
    containers = get_fields(parent)

    # Consulta para obtener solo los campos `id` y `name`
    #fields_list = db.session.query(Field.id, Field.name).filter_by(container_id=record_id).all()
    record = application.getContainerDetails(record_id)
    fields_list = record.fields

    # Convertir el resultado en una lista de diccionarios (opcional)
    container_fields = [{"id": field.id, "name": field.name} for field in fields_list]
    return render_template('backend/base/view_container.html', institution=institution,backlink=backlink, containers=containers,classname=classname, container_fields=container_fields, class_names=class_names)

@blueprintname.route(f'/develop/{classname}/<int:record_id>/edit/', methods=['GET', 'POST'])
@traceError
@login_required
def edit_record(record_id):
    class_names = application.list_class_names()
    institution = Record.query.get_or_404(record_id)
    backlink = request.args.get("backlink")
    containers = get_fields(parent)
    if request.method == 'POST':
        session.saveForm(institution,containers) 
                
        db.session.commit()
        flash('La institución ha sido actualizada exitosamente.', 'success')
        return render_template('backend/base/edit_base.html', institution=institution, containers=containers,classname=classname, class_names=class_names,backlink=backlink)
    return render_template('backend/base/edit_base.html', institution=institution,containers=containers,classname=classname, class_names=class_names,backlink=backlink)

@blueprintname.route(f'/develop/{classname}/<int:record_id>/delete/', methods=['POST'])
@traceError
@login_required
def delete_record(record_id):
    institution = Record.query.get_or_404(record_id)
    backlink = request.args.get("backlink")
    db.session.delete(institution)
    db.session.commit()
    flash('La institución ha sido eliminada exitosamente.', 'success')
    return redirect(url_for('.list_record'))  # Asumiendo que existe una ruta para listar instituciones

@blueprintname.route(f'/develop/{classname}/all/')
@traceError
@login_required
def list_record():
    class_names = application.list_class_names()
    backlink = request.args.get("backlink")
    institutions = Record.query.all()  # Consulta todas las instituciones
    return render_template('backend/base/list_base.html', institutions=institutions,classname=classname, class_names=class_names,backlink=backlink)