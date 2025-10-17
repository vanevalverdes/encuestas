
from utils.packages import application, session, engine
from utils.packages.engine import traceError
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask import session as Session
from datetime import datetime, timedelta, timezone
import json
from werkzeug.utils import secure_filename
import os
import requests
import hashlib


blueprintname = Blueprint("api", __name__)
slug = "api"


@blueprintname.route(f'/{slug}/')
def index():
    return "API"
