from models.develop.relevant import Relevant, get_fields

from utils.methods import application, session
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from utils.db import db
from werkzeug.utils import secure_filename
from flask_login import login_required
import os
blueprintname = Blueprint("relevant", __name__)

classname = "relevant"
Record = Relevant
parent = False


@blueprintname.route(f'/develop/{classname}/new/', methods=["GET","POST"])
@login_required
def create_record():
    class_names = application.list_class_names()
    parent = request.args.get('parent')
    print(parent)
    containers = get_fields(parent)
    print(containers)
    
    if request.method == "GET":
        return render_template("backend/base/new_base.html", containers=containers,classname=classname, class_names=class_names)
    elif request.method == "POST":

        new_institution = Record()
        session.saveForm(new_institution,containers) 

        db.session.add(new_institution)
        db.session.commit()

        return redirect(url_for('.view_record', record_id=new_institution.id,classname=classname, class_names=class_names))
    
@blueprintname.route(f'/develop/{classname}/<int:record_id>')
@login_required
def view_record(record_id):
    class_names = application.list_class_names()
    institution = Record.query.get_or_404(record_id)
    containers = get_fields()

    return render_template('backend/base/view_base.html', institution=institution, containers=containers,classname=classname,  class_names=class_names)

@blueprintname.route(f'/develop/{classname}/<int:record_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    class_names = application.list_class_names()
    institution = Record.query.get_or_404(record_id)
    containers = get_fields(parent)
    if request.method == 'POST':
        session.saveForm(institution,containers) 
                
        db.session.commit()
        flash('La institución ha sido actualizada exitosamente.', 'success')
        return render_template('backend/base/edit_base.html', institution=institution, containers=containers,classname=classname, class_names=class_names)
    return render_template('backend/base/edit_base.html', institution=institution,containers=containers,classname=classname, class_names=class_names)

@blueprintname.route(f'/develop/{classname}/<int:record_id>/delete/', methods=['POST'])
@login_required
def delete_record(record_id):
    institution = Record.query.get_or_404(record_id)
    db.session.delete(institution)
    db.session.commit()
    flash('La institución ha sido eliminada exitosamente.', 'success')
    return redirect(url_for('.list_record'))  # Asumiendo que existe una ruta para listar instituciones

@blueprintname.route(f'/develop/{classname}/all/')
@login_required
def list_record():
    class_names = application.list_class_names()
    institutions = Record.query.all()  # Consulta todas las instituciones
    return render_template('backend/base/list_base.html', institutions=institutions,classname=classname, class_names=class_names)