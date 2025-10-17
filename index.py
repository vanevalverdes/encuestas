# MIT License
# Copyright (c) 2025 Nible Tecnología en Desarrollo LTDA
# See LICENSE file for more details.

from app import create_app
from utils.db import db
from flask_mail import Mail
from urllib.parse import urlencode
from utils.jinja_extends import setup_jinja2
from version import __version__ 
SYSTEM_VERSION = __version__

app = create_app()
mail = Mail(app)

@app.context_processor
def inject_version():
    return {'version': SYSTEM_VERSION} 

setup_jinja2(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000, use_reloader=False)
