from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from utils.db import db

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    name = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    _reset_token = db.Column(db.String(255))
    _token_expiration = db.Column(db.DateTime)
    _password_hash = db.Column(db.String(255))
    usergroup_id = db.Column(db.Integer, db.ForeignKey('usergroup.id'))
    usergroup = db.relationship('Usergroup', backref='users')

    def __repr__(self) -> str:
        return f"{self.email}"
    
    def set_password(self, password):
        self._password_hash = generate_password_hash(password)


def get_fields():
    from utils.methods import application
    clazzes = application.getAllUsergroups()
    options = [{"label": usergroup.name, "value": usergroup.id} for usergroup in clazzes if usergroup.id != 1]
    fields = {
        "GeneralInfo":{
            "class":"col-sm-4",
            "title":"Identificacion",
            "fields":{
                "id": {
                    "id": "id", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Id", 
                    "input": "integer",
                    "class":""
                },
                "name": {
                    "id": "name", 
                    "type": "String", 
                    "maxlength": "100", 
                    "label": "Nombre", 
                    "input": "text",
                    "class":""
                },
                "lastname": {
                    "id": "lastname", 
                    "type": "String", 
                    "maxlength": "100", 
                    "label": "Apellido", 
                    "input": "text",
                    "class":""
                },
                "email": {
                    "id": "email", 
                    "type": "String", 
                    "maxlength": "100", 
                    "label": "Usuario", 
                    "input": "text",
                    "class":""
                },
                "usergroup_id": {
                    "id": "usergroup_id", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Tipo de Usuario", 
                    "input": "select",
                    "class":"",
                    "options":options
                }
            }
        }
    }
    return fields