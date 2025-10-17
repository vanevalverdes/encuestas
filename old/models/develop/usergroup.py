from utils.db import db

class Usergroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)

    def __repr__(self) -> str:
        return f"{self.name}"

def get_fields():
    fields = {
        "GeneralInfo":{
            "class":"col-sm-6",
            "title":"Configuración",
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
                "description": {
                    "id": "description", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Descripcion", 
                    "input": "textarea",
                    "class":""
                }
            }
        }
    }
    return fields