from config import url as mainUrl, applicationName, adminMail

def traceError(f):
    from functools import wraps
    import traceback
    from flask import request, render_template_string
    from flask_login import current_user
    from datetime import datetime
    from werkzeug.exceptions import Unauthorized  # Importamos esta excepción

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Unauthorized:
            # Este error se lanza cuando el usuario no está logueado y la vista requiere login
            return "Necesitas iniciar sesión para acceder a esta página.", 401
        except Exception as e:
            error_message = traceback.format_exc()
            error_url = request.url
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Mostrar error en consola
            print("⚠️ Error en la aplicación:")
            print(f"URL: {error_url}")
            print(error_message)

            # Guardar error en archivo de log
            with open("error.log", "a") as error_file:
                error_file.write(f"[{timestamp}] Error en URL: {error_url}\n{error_message}\n\n")

            # Enviar correo al administrador
            mail_message = f"""
            <h2>Error en la aplicación</h2>
            <p><strong>Fecha y hora:</strong> {timestamp}</p>
            <p><strong>URL:</strong> {error_url}</p>
            <pre style="background:#f8f8f8;padding:10px;border:1px solid #ddd;">{error_message}</pre>
            """

            send_email_from_db(
                adminMail,
                f"[{applicationName}] Error en la aplicación",
                mail_message
            )

            # Verificar si el usuario está autenticado y es admin (usergroup == 1)
            if hasattr(current_user, "usergroup_id") and current_user.usergroup_id == 1:
                error_template = """
                <h2>Ha ocurrido un error inesperado</h2>
                <p><strong>URL:</strong> {{ url }}</p>
                <pre style="background:#f0f0f0;padding:10px;border:1px solid #ccc;">{{ error }}</pre>
                <p>Este detalle solo es visible para administradores.</p>
                """
                return render_template_string(error_template, url=error_url, error=str(e)), 500

            # Para usuarios normales, solo mensaje genérico
            return "Ha ocurrido un error. Por favor, contacta al administrador.", 500

    return decorated_function

def strToDate(date_str, format='%Y-%m-%d'):
    from datetime import datetime
    try:
        return datetime.strptime(date_str, format)
    except ValueError as e:
        print(f"Error converting date: {e}")
        return None

def dateToStr(date_obj, format='%Y-%m-%d'):
    from datetime import datetime
    try:
        return date_obj.strftime(format)
    except Exception as e:
        print(f"Error converting datetime to string: {e}")
        return None
    
def random(length=12):
    import random
    import string
    # Define los caracteres que deseas incluir en la cadena aleatoria
    characters = string.ascii_letters + string.digits
    # Genera la cadena aleatoria
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def now():
    from datetime import datetime, timezone 
    now = datetime.now(timezone.utc)
    return now

def createQR(id, token):
    import qrcode
    import os
    
    # Crea la URL que se incrustará en el QR
    qr_url = f"{mainUrl}/validation/{id}/{token}"

    # Genera el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    # Convierte el QR a una imagen
    img = qr.make_image(fill_color="black", back_color="white")

    # Define la ruta donde se guardará la imagen
    img_path = os.path.join('static', 'qrcodes', f'qr_{id}.png')
    img.save(img_path)

    return img_path

def send_email(to, subject, template, **kwargs):
    import smtplib
    import traceback
    from flask_mail import Message
    from flask import render_template
    from index import app, mail

    with app.app_context():
        try:
            msg = Message(subject, recipients=[to])
            msg.html = render_template(template, **kwargs)
            mail.send(msg)
            print(f"Correo enviado a {to}")

        except smtplib.SMTPRecipientsRefused as e:
            error_message = f"[ERROR] Correo rebotado: {to} - {e}\n"
            print(error_message)

        except Exception as e:
            error_message = f"[ERROR] Fallo al enviar correo a {to}: {e}\n{traceback.format_exc()}"
            print(error_message)

            # Guardar el error en un archivo de log
            with open("email_errors.log", "a") as error_file:
                error_file.write(error_message + "\n")
                
def send_email_from_db(to, subject, template, **kwargs):
    import smtplib
    from flask_mail import Message
    import traceback
    from flask import render_template, render_template_string
    from index import app, mail

    with app.app_context():
        try:
            msg = Message(subject, recipients=[to])
            msg.html = render_template_string(template, **kwargs)
            mail.send(msg)
            print(f"Correo enviado a {to}")

        except smtplib.SMTPRecipientsRefused as e:
            error_message = f"[ERROR] Correo rebotado: {to} - {e}\n"
            print(error_message)

        except Exception as e:
            error_message = f"[ERROR] Fallo al enviar correo a {to}: {e}\n{traceback.format_exc()}"
            print(error_message)

        # Guardar error en un archivo de log
            with open("email_errors.log", "a") as error_file:
                error_file.write(error_message + "\n")

def send_reset_email(email, link):
    from flask_mail import Message
    from flask import render_template
    from index import app, mail
    with app.app_context():
        subject = "Cambio de Contraseña"
        msg = Message(subject, recipients=[email])
        msg.body = f"""
        Recibimos una solicitud de cambio de contraseñe, para continuar visite el siguiente enlace:

        {link}

        Si ud no realizó esta solicitud, ignore este mensaje.
        """
        mail.send(msg)

def moneyValuesToView(containers, record):
    money_fields = {key for container_key, container in containers.items()
            for key, value in container['fields'].items() if value['type'] == 'Money'}
    fieldsToView = {}
    for field in money_fields:
        if hasattr(record, field) and getattr(record, field) is not None:
            val = intToFloat(getattr(record, field))
            fieldsToView[field] = val / 100
        else:
            fieldsToView[field] = 00
    print(fieldsToView)
    return fieldsToView

def newMoney(value):
    return Money(value)

def intToFloat(value):
    return float(value)

def floatToMoney(value):
    valueRound = round(value,2)
    return Money(int(valueRound * 100))

class Money:
    def __init__(self, value):
        self.cents = int(value)

    def __repr__(self):
        return f"Money({self.cents})Cents"

    def getCents(self):
        cents = int(self.cents)
        return cents
    def format(self, locale_setting=False,symbol=False,grouping=True):
        import locale
        if not locale_setting:
            locale_setting='en_US.UTF-8'
        else:
            # Configurar la localización monetaria
            # Latinoamerica: es-419
            # Costa Rica: es-CR
            # Chile: es-CL
            # Mexico: es-MX
            locale_setting = f"{locale_setting}.UTF-8"
        locale.setlocale(locale.LC_MONETARY, locale_setting)
        valueFormat = self.cents / 100
        return locale.currency(valueFormat,symbol,grouping)

def formatJSON(data):
    import json
    return json.dumps(data, indent=4)
