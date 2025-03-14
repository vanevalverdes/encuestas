
from utils.methods import application, session, engine
from utils.methods.engine import traceError
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask import session as Session
from datetime import datetime, timedelta, timezone
import json
from werkzeug.utils import secure_filename
import os
import requests
import hashlib


blueprintname = Blueprint("webhooks", __name__)


@blueprintname.route(f'/response/', methods=["POST"])
@traceError
def receive_callback_payme():
    import traceback
    try:
        purchaseVerification = request.form.get("purchaseVerification")
        authorizationResult = request.form.get("authorizationResult")
        authorizationCode = request.form.get("authorizationCode")

        return render_template('frontend/paymentResult.html')
    except Exception as e:
        error_message = traceback.format_exc()
        mailMessage = "<p>Ocurrió un error:<br>{{error_message_variable}}</p>"
        engine.send_email_from_db("vane@nibletecnologia.com","Error en pagos",mailMessage,error_message_variable=error_message)





