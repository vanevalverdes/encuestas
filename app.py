from flask import Flask

from utils.db import db
from routes.develop import container, field, user, clazz, application, relevant, usergroup
from flask_migrate import Migrate
from config import Config
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from models.develop.user import User
from models.production import clazzlist


# Importa las Rutas de clases
from routes import routing



# Define Login Manager 
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Inicializa el app
def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    login_manager.init_app(app)

    # Importa los Blueprint al app
    app.register_blueprint(user.blueprintname)
    app.register_blueprint(field.blueprintname)
    app.register_blueprint(container.blueprintname)
    app.register_blueprint(application.blueprintname)
    app.register_blueprint(clazz.blueprintname)
    app.register_blueprint(relevant.blueprintname)
    app.register_blueprint(usergroup.blueprintname)
    app.register_blueprint(routing.blueprintname)


    return app
