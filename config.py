# MIT License
# Copyright (c) 2025 Nible Tecnología en Desarrollo LTDA
# See LICENSE file for more details.

from pathlib import Path
from dotenv import load_dotenv
import os

# Cargar variables del .env
load_dotenv()

develop = True
databaseType = os.getenv("DATABASE_TYPE")
applicationName = os.getenv("APPLICATION_NAME")
adminMail = os.getenv("ADMIN_MAIL")


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


# Construir la URI de la base de datos
# Construir la URI de la base de datos
MYSQL_USER = f'{os.getenv("MYSQL_USER")}'
MYSQL_PASSWORD = f'{os.getenv("MYSQL_PASSWORD")}'
MYSQL_HOST = f'{os.getenv("MYSQL_HOST")}'
MYSQL_PORT = f'{os.getenv("MYSQL_PORT")}'
MYSQL_DB = f'{os.getenv("MYSQL_DB")}'
class Config:
    if develop:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        MAIL_SERVER = os.getenv("MAIL_SERVER")
        MAIL_PORT = int(os.getenv("MAIL_PORT"))
        MAIL_USE_TLS = False
        MAIL_USE_SSL = True
        MAIL_USERNAME = os.getenv("MAIL_USERNAME")
        MAIL_PASSWORD = f'{os.getenv("MAIL_PASSWORD")}'
        MAIL_DEFAULT_SENDER = ('UC-LAC - Uni-Co CMS', MAIL_USERNAME)
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        MAIL_SERVER = os.getenv("MAIL_SERVER")
        MAIL_PORT = int(os.getenv("MAIL_PORT"))
        MAIL_USE_TLS = False
        MAIL_USE_SSL = True
        MAIL_USERNAME = os.getenv("MAIL_USERNAME")
        MAIL_PASSWORD = f'{os.getenv("MAIL_PASSWORD")}'
        MAIL_DEFAULT_SENDER = ('Reservaciones', MAIL_USERNAME)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 1800 
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    SECRET_KEY = os.getenv("SECRET_KEY")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    STATIC_FOLDER = os.getenv("STATIC_FOLDER")
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 100 MB

    
