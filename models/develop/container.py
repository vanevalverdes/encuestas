# -*- coding: utf-8 -*-
from utils.db import db
from sqlalchemy.orm import backref


class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    title = db.Column(db.String(255))
    extraclass = db.Column(db.String(255))
    type = db.Column(db.String(255))
    connected_table = db.Column(db.Integer)
    connected_table_fields = db.Column(db.Text)
    clazz_id = db.Column(
        db.Integer,
        db.ForeignKey('clazz.id', ondelete='CASCADE')
    )

    clazz = db.relationship(
        'Clazz',
        backref=backref(
            'containers',
            cascade='all, delete-orphan',
            passive_deletes=True
        )
    )
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
    
    def __repr__(self) -> str:
        return f"{self.name}"    
    
    
def get_fields(parent):
    from utils.packages import application
    clazzes = application.list_class_names()
    options = [{"label": "Ninguna", "value": ""}] + [{"label": name, "value": id} for id, name in clazzes]
    if parent:
        parent = parent
    else:
        parent = "" 
    fields = {
        "GeneralInfo": {
            "class": "col-sm-12",
            "title": "Configuración",
            "fields": {
                "id": {
                    "id": "id",
                    "type": "Integer",
                    "maxlength": "",
                    "label": "Id",
                    "input": "integer",
                    "class": ""
                },
                "name": {
                    "id": "name",
                    "type": "String",
                    "maxlength": "100",
                    "label": "Nombre",
                    "input": "text",
                    "class": ""
                },
                "title": {
                    "id": "title",
                    "type": "String",
                    "maxlength": "255",
                    "label": "Título para mostrar",
                    "input": "text",
                    "class": ""
                },
                "type": {
                    "id": "type",
                    "type": "String",
                    "maxlength": "255",
                    "label": "Título para mostrar",
                    "input": "select",
                    "options": [{"label": "Row", "value": "row"},{"label": "Tab", "value": "tab"}] ,
                    "class": ""
                },
                "clazz_id": {
                    "id": "clazz_id",
                    "type": "Integer",
                    "maxlength": "",
                    "label": "Clase a la que pertenece",
                    "input": "parent",
                    "class": "disabled",
                    "value": parent
                },
                "extraclass": {
                    "id": "extraclass",
                    "type": "String",
                    "maxlength": "255",
                    "label": "Clases CSS Adicionales",
                    "input": "text",
                    "class": ""
                },
                "connectedTable": {
                    "id": "connected_table",
                    "type": "Integer",
                    "maxlength": "255",
                    "label": "Tabla Conectada",
                    "input": "select",
                    "options": options,
                    "class": ""
                },
                "connectedTableFields": {
                    "id": "connected_table_fields",
                    "type": "Text",
                    "maxlength": "",
                    "label": "Campos a mostrar en Tabla Conectada",
                    "input": "textarea",
                    "class": ""
                }
            }
        }
    }
    
    return fields

