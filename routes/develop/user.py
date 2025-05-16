from models.develop.user import User, get_fields
from utils.methods import application, session
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
auth = [1,2]
def authorization():
    if current_user.usergroup.id in auth:
        return True
    return False

@blueprintname.route(f'/{classname}/new/', methods=["GET","POST"])
@login_required
def create_record():
    if authorization():
        containers = get_fields()
        class_names = application.list_class_names()
        if request.method == "GET":
            return render_template("backend/base/new_user.html", containers=containers,classname=classname, class_names=class_names)
        elif request.method == "POST":

            new_institution = Record()
            session.saveForm(new_institution,containers)
            pwd = request.form["password"]
            new_institution.set_password(pwd)
            db.session.add(new_institution)
            db.session.commit()

            return redirect(url_for('.view_record', record_id=new_institution.id,classname=classname, class_names=class_names))
        return redirect(url_for('application.index'))
    
@blueprintname.route(f'/{classname}/<int:record_id>')
@login_required
def view_record(record_id):
    if authorization():
        containers = get_fields()
        class_names = application.list_class_names()
        institution = Record.query.get_or_404(record_id)
        return render_template('backend/base/view_base.html', institution=institution, containers=containers,classname=classname, class_names=class_names)
    return redirect(url_for('application.index'))

@blueprintname.route(f'/{classname}/<int:record_id>/edit/', methods=['GET', 'POST'])
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

@blueprintname.route(f'/{classname}/<int:record_id>/delete/', methods=['POST'])
@login_required
def delete_record(record_id):
    if authorization():
        class_names = application.list_class_names()
        institution = Record.query.get_or_404(record_id)
        db.session.delete(institution)
        db.session.commit()
        flash('La institución ha sido eliminada exitosamente.', 'success')
        return redirect(url_for('.list_record'))  
    return redirect(url_for('application.index'))

@blueprintname.route(f'/{classname}/all/')
@login_required
def list_record():
    if authorization():
        class_names = application.list_class_names()
        
        #list = [
        #    "supervisor01@opolconsultores.com",
        #    "supervisor02@opolconsultores.com",
        #    "supervisor03@opolconsultores.com",
        #    "supervisor04@opolconsultores.com",
        #    "supervisor05@opolconsultores.com"
        #]
        #password = "supervisor25mayo*"
        #hashed_password = generate_password_hash(password)
        #print(hashed_password)
        #for item in list:
        #    new = Record()
        #    setattr(new, "name", item)
        #    setattr(new, "lastname", item)
        #    setattr(new, "email", item)
        #    setattr(new, "usergroup_id", 2)
        #    setattr(new, "_password_hash", hashed_password)
        #    db.session.add(new)
        #db.session.commit()
        password = "encuesta25mayo*"
        hashed_password = generate_password_hash(password)
        #institutions = Record.query.all() 
        institutions = Record.query.filter(Record.usergroup_id != 1).all()
        for item in institutions:
            setattr(item, "_password_hash", hashed_password)
            db.session.commit()
        return render_template('backend/base/list_user.html', institutions=institutions,classname=classname, class_names=class_names)
    return redirect(url_for('application.index'))

@blueprintname.route(f'/import/agency/')
@login_required
def import_class():
    class_names = application.list_class_names()
    """
    for id in range(34,41):
        record = session.getRecord("order",id)
        if record:
            for ol in record.orderlines:
                db.session.delete(ol) 
            db.session.delete(record) 
    db.session.commit()
   

    products = session.getTable("Product").all()
    for p in products:
        record = session.getRecord("Product",p.id)
        record.store("public",True)
    products = session.getTable("Variation").all()
    for p in products:
        record = session.getRecord("Variation",p.id)
        record.store("public",True)
    products = session.getTable("Subvariation").all()
    for p in products:
        record = session.getRecord("Subvariation",p.id)
        record.store("public",True)
         """
    # Obtener todas las instancias de Agency
    #all_agencies = Agencycontact.query.all()

    # Iterar sobre cada instancia y eliminarla
   #for agency in all_agencies:
    #   db.session.delete(agency)

    # Confirmar los cambios en la base de datos
    #db.session.commit()
    """
    listCommma = list.split('\n')
    for item in listCommma:
        parts = item.split(";")
        print(parts)
        new = Agencycontact()
        setattr(new, "name", parts[0])
        setattr(new, "phone", parts[1])
        setattr(new, "email", parts[2])
        setattr(new, "agency_id", parts[3])
        db.session.add(new)
    db.session.commit()
    """
    #institutions = Record.query.all() 
    #institutions = Record.query.filter(Record.usergroup_id != 1).all() 
    #return render_template('backend/base/list_user.html', institutions=institutions,classname=classname, class_names=class_names)
    return redirect(url_for('application.index'))
