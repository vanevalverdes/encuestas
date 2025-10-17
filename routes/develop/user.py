from models.develop.user import User, get_fields, get_fields_form
from utils.packages import application, session
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from utils.db import db
from werkzeug.utils import secure_filename
from flask_login import login_required
from flask_login import current_user
from werkzeug.security import generate_password_hash
import os

classname = "user"
Record = User

blueprintname = Blueprint("user", __name__)
auth = [1]
def authorization():
    if current_user.usergroup.id in auth:
        return True
    return False

@blueprintname.route(f'/admin/{classname}/new/', methods=["GET","POST"])
@login_required
def create_record():
    if authorization():
        containers = get_fields()
        fields = get_fields_form()
        class_names = application.list_class_names()
        if request.method == "GET":
            return render_template("backend/base/new_user.html", containers=containers,classname=classname, class_names=class_names)
        elif request.method == "POST":

            new_institution = Record()
            session.saveForm(new_institution,fields)
            pwd = request.form["password"]
            new_institution.set_password(pwd)
            db.session.add(new_institution)
            db.session.commit()

            return redirect(url_for('.view_record', record_id=new_institution.id,classname=classname, class_names=class_names))
        return redirect(url_for('frontend.index'))
    
@blueprintname.route(f'/admin/{classname}/<int:record_id>')
@login_required
def view_record(record_id):
    if authorization():
        containers = get_fields()
        class_names = application.list_class_names()
        institution = Record.query.get_or_404(record_id)
        return render_template('backend/base/view_base.html', institution=institution, containers=containers,classname=classname, class_names=class_names)
    return redirect(url_for('frontend.index'))

@blueprintname.route(f'/admin/{classname}/<int:record_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    if authorization():
        containers = get_fields()
        class_names = application.list_class_names()
        institution = Record.query.get_or_404(record_id)
        if request.method == 'POST':
            session.saveForm(institution,containers)
            pwd = request.form["password"]
            if pwd:
                institution.set_password(pwd)
            db.session.commit()
            flash('La institución ha sido actualizada exitosamente.', 'success')
            return render_template('backend/base/edit_user.html', institution=institution, containers=containers,classname=classname, class_names=class_names)
        return render_template('backend/base/edit_user.html', institution=institution,containers=containers,classname=classname, class_names=class_names)

@blueprintname.route(f'/admin/{classname}/<int:record_id>/delete/', methods=['POST'])
@login_required
def delete_record(record_id):
    if authorization():
        class_names = application.list_class_names()
        institution = Record.query.get_or_404(record_id)
        db.session.delete(institution)
        db.session.commit()
        flash('La institución ha sido eliminada exitosamente.', 'success')
        return redirect(url_for('.list_record'))  
    return redirect(url_for('frontend.index'))

@blueprintname.route(f'/admin/{classname}/all/')
@login_required
def list_record():
    if authorization():
        class_names = application.list_class_names()
        institutions = Record.query.filter(Record.usergroup_id != 1).all()
        return render_template('backend/base/list_user.html', institutions=institutions,classname=classname, class_names=class_names)
    return redirect(url_for('frontend.index'))
