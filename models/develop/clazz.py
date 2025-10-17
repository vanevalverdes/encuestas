# -*- coding: utf-8 -*-
from utils.db import db

class Clazz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    label = db.Column(db.String(255))
    tag = db.Column(db.String(255))
    treeView = db.Column(db.String(255))
    template = db.Column(db.String(255))
    plural = db.Column(db.String(255))
    sort_field_results = db.Column(db.String(255))
    table_fields = db.Column(db.Text)
    search_fields = db.Column(db.Text)
    clazz_representation = db.Column(db.Text)
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
    
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
                    "label": "Nombre de la Clase en BD", 
                    "input": "text",
                    "class":""
                },
                "label": {
                    "id": "label", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Etiqueta para mostrar", 
                    "input": "text",
                    "class":""
                },
                "plural": {
                    "id": "plural", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Plural (hace referencia para tablas conectadas)", 
                    "input": "text",
                    "class":""
                },
                "template": {
                    "id": "template", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Plantilla", 
                    "input": "text",
                    "class":""
                },
                "treeView": {
                    "id": "treeView", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Nombre de campo para Vista de Árbol", 
                    "input": "text",
                    "class":""
                }
            }
        },
        "ConnectedInfo":{
            "class":"col-sm-6",
            "title":"Configuración de visualización",
            "fields":{
                "clazz_representation": {
                    "id": "clazz_representation", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Representación: (|title| ,|id|)", 
                    "input": "textarea",
                    "class":""
                },
                "search_fields": {
                    "id": "search_fields", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Listado de campos para busqueda (id,created_at)", 
                    "input": "textarea",
                    "class":""
                },
                "sort_field_results": {
                    "id": "sort_field_results",
                    "type": "String", 
                    "maxlength": "", 
                    "label": "Ordenar por (fieldname|sort asc or desc) Ej: created_at|desc", 
                    "input": "text",
                    "class":""
                },
                "table_fields": {
                    "id": "table_fields", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Listado de campos para tabla (ID|id,Fecha|created_at)", 
                    "input": "textarea",
                    "class":""
                }
            }
        }
    }
    return fields
def get_fields_form():
    fields = {
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
                "label": {
                    "id": "label", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Etiqueta para mostrar", 
                    "input": "text",
                    "class":""
                },
                "plural": {
                    "id": "plural", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Plural (hace referencia para tablas conectadas)", 
                    "input": "text",
                    "class":""
                },
                "template": {
                    "id": "template", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Plantilla", 
                    "input": "text",
                    "class":""
                },
                "clazz_representation": {
                    "id": "clazz_representation", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Representación: (|title| ,|id|)", 
                    "input": "textarea",
                    "class":""
                },
                "search_fields": {
                    "id": "search_fields", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Listado de campos para busqueda (id,created_at)", 
                    "input": "textarea",
                    "class":""
                },
                "sort_field_results": {
                    "id": "sort_field_results",
                    "type": "String", 
                    "maxlength": "", 
                    "label": "Ordenar por (fieldname|sort asc or desc) Ej: created_at|desc", 
                    "input": "text",
                    "class":""
                },
                "table_fields": {
                    "id": "table_fields", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Listado de campos para tabla (ID|id,Fecha|created_at)", 
                    "input": "textarea",
                    "class":""
                },
                "treeView": {
                    "id": "treeView", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Nombre de campo para Vista de Árbol", 
                    "input": "text",
                    "class":""
                }
            }

    return fields
