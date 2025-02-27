from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_from_directory
from models.develop.user import User
from utils.methods.application import isPublic,list_class_names, getMenu
from utils.methods.engine import traceError, random, now, send_reset_email
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from utils.db import db
from flask import session as Session

blueprintname = Blueprint("application", __name__)


@blueprintname.route('/')
@traceError
def index():
    if current_user.is_authenticated:
        class_names = list_class_names()
        return render_template("backend/template.html",class_names=class_names)
    return render_template('frontend/index.html')
    
@blueprintname.route('/admin/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=username).first()
        
        if user and check_password_hash(user._password_hash, password):
            login_user(user, remember=True)
            usergroup = current_user.usergroup_id
            #menu = getMenu(usergroup)
            #Session["menu"] = menu
            return redirect(url_for('.index'))  # Asumiendo que tienes una ruta 'dashboard'
            #return "Todo en orden"
        elif user:
            flash('Contraseña incorrecta')
        else:
            flash('Email incorrecto')
    return render_template('backend/base/login.html')

@blueprintname.route('/admin/logout/')
@traceError
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))

@blueprintname.route('/blob/<filename>')
@traceError
def uploaded_file(filename):
    fieldname = request.args.get('fieldname')
    classname = request.args.get('classname')
    record = request.args.get('record')
    
    if fieldname and classname:
        if current_user.is_authenticated or isPublic(fieldname, classname):
            # Construir el path al archivo utilizando el valor de record
            directory = f"{current_app.config['UPLOAD_FOLDER']}/{record}"
            return send_from_directory(directory, filename)
    return "", 403  # Retornar 403 Forbidden si no está autorizado


@blueprintname.route('/admin/reset_password/', methods=["GET", "POST"])
def reset_password_request():
    if request.method == "POST":
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(user.email, salt="asd;ljasll2asdas")
            user._reset_token = token
            user._token_expiration = now() + timedelta(hours=1)
            db.session.commit()
            link = url_for('.reset_password', token=token, _external=True)
            send_reset_email(user.email, link)
            flash('An email has been sent with instructions to reset your password.', 'info')
        else:
            flash('Email address not found.', 'danger')
        return redirect(url_for('.reset_password_request'))
    return render_template("frontend/reset_password_request.html")

@blueprintname.route('/admin/reset_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='asd;ljasll2asdas', max_age=3600)  # 1 hour validity
    except:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('.reset_password_request'))
    
    user = User.query.filter_by(email=email).first()
    if not user or user._reset_token != token:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('.reset_password_request'))
    
    if request.method == "POST":
        password = request.form.get("password")
        user.set_password(password)
        user._reset_token = None  # Invalidate the token
        user._token_expiration = None
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('application.login'))  # Redirigir a la página de inicio de sesión

    return render_template("frontend/reset_password.html", token=token)