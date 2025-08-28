from pathlib import Path
import os

develop = True
databaseType = "mysql"
applicationName = "Opol Sistema"
adminMail = "vane@nibletecnologia.com"


base_dir = str(Path(__file__).parent.resolve())


if develop:
    # Ruta completa al ejecutable flask
    flask_executable = 'flask'

    # Configuración para Windows, asegúrate de que la ruta es correcta
    wkhtml = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    
    url = "http://127.0.0.1:5000"
else:
    # Ruta completa al ejecutable flask en VM
    flask_executable = '/root/landing-maps/develop/venv/bin/flask'

    # Instalar en Linux: sudo apt-get install wkhtmltopdf
    # Verificar para Linux: which wkhtmltopdf
    wkhtml = '/usr/bin/wkhtmltopdf'
    
    url = "http://143.244.187.247"

# Ruta del sitio

class Config:
    if develop:
        # En caso de usar SQLite
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://encuestas25opol_root:^tXoz7BvetJx@23.235.193.87:3306/encuestas25opol_production'
        #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://mapavrtx_mapuso:qhQh%9YBy8NM@158.69.145.101:3306/mapavrtx_dbmapu?charset=utf8mb4'
        #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ilamdocs24_mapuso:CFiCc*NadFnJ@198.46.85.8:3306/ilamdocs24_mapu?charset=utf8mb4'
        MAIL_SERVER = 'smtp.hostinger.com'
        MAIL_PORT = 465
        MAIL_USE_TLS = False
        MAIL_USE_SSL = True
        MAIL_USERNAME = 'noreply@nibletecnologia.com'
        MAIL_PASSWORD = 'TwinPeaks2024.'
        MAIL_DEFAULT_SENDER = ('Pruebas NGDO', 'noreply@nibletecnologia.com')
    else:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://encuestas25opol_root:^tXoz7BvetJx@23.235.193.87:3306/encuestas25opol_production'
        MAIL_SERVER = 'smtp.hostinger.com'
        MAIL_PORT = 465
        MAIL_USE_TLS = False
        MAIL_USE_SSL = True
        MAIL_USERNAME = 'noreply@nibletecnologia.com'
        MAIL_PASSWORD = 'TwinPeaks2024.'
        MAIL_DEFAULT_SENDER = ('Pruebas NGDO', 'noreply@nibletecnologia.com')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 1800 
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    SECRET_KEY = 'lghaasdñas5654132aa35r.*'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    
