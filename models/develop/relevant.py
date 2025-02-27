from utils.db import db

class Relevant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search = db.Column(db.Boolean)
    create = db.Column(db.Boolean)
    edit = db.Column(db.Boolean)
    delete = db.Column(db.Boolean)
    read = db.Column(db.Boolean)
    usergroup_id = db.Column(db.Integer, db.ForeignKey('usergroup.id'))
    usergroup = db.relationship('Usergroup', backref='relevants')
    clazz_id = db.Column(db.Integer, db.ForeignKey('clazz.id'))
    clazz = db.relationship('Clazz', backref='relevants')
    
    def __repr__(self) -> str:
        return f"{repr(self.clazz)} - {repr(self.usergroup)}"
    
def get_fields(parent=False):
    from utils.methods import application
    clazzes = application.list_class_names()
    usergroups = application.getAllUsergroups()
    usergroupsOptions = [{"label": "Ninguno", "value": ""}] + [{"label": relevant.name, "value": relevant.id} for relevant in usergroups]
    clazzesOptions = [{"label": "Ninguna", "value": ""}] + [{"label": name, "value": id} for id, name in clazzes]
    if parent:
        parent = [{"label": "Parent", "value": parent}]
    else:
        parent = "" 
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
                    "label": "Nombre de la Clase en BD", 
                    "input": "text",
                    "class":""
                },
                "search": {
                    "id": "search", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Buscar", 
                    "input": "checkbox",
                    "class":""
                },
                "create": {
                    "id": "create", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Crear", 
                    "input": "checkbox",
                    "class":""
                },
                "edit": {
                    "id": "edit", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Editar", 
                    "input": "checkbox",
                    "class":""
                },
                "delete": {
                    "id": "delete", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Borrar", 
                    "input": "checkbox",
                    "class":""
                },
                "read": {
                    "id": "read", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Leer", 
                    "input": "checkbox",
                    "class":""
                },
                "usergroup_id": {
                    "id": "usergroup_id", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Usergroup", 
                    "input": "select",
                    "options": usergroupsOptions,
                    "class":""
                },
                "clazz_id": {
                    "id": "clazz_id", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Clase", 
                    "input": "select",
                    "options": parent or clazzesOptions,
                    "class":""
                }
            }
        }
    }
    return fields