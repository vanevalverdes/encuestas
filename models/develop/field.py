# -*- coding: utf-8 -*-
from utils.db import db
from sqlalchemy.orm import backref

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    name = db.Column(db.String(100))
    maxlength = db.Column(db.Integer)
    connected_table = db.Column(db.Integer)
    label = db.Column(db.String(100))
    input = db.Column(db.String(100))
    sort = db.Column(db.String(100))
    required = db.Column(db.Boolean)
    hidden = db.Column(db.Boolean)
    publicBlob = db.Column(db.Boolean)
    default_value = db.Column(db.Text)
    select_options = db.Column(db.Text)
    extraclass = db.Column(db.String(255))
    hasManyValues = db.Column(db.Boolean)
    readOnly = db.Column(db.Boolean)
    calculate_file = db.Column(db.String(255))
    calculate_function = db.Column(db.String(255))
    helper = db.Column(db.String(255))
    clazz_id = db.Column(
        db.Integer,
        db.ForeignKey('clazz.id', ondelete='CASCADE')
    )
    clazz = db.relationship(
        'Clazz',
        backref=backref(
            'fields',
            cascade='all, delete-orphan',
            passive_deletes=True
        ),
        order_by="Field.sort.asc()"
    )
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    def __repr__(self) -> str:
        return f"{self.name}"

def get_fields(parent=False):
    fields_form = get_fields_form(parent)
    fields = {
        "GeneralInfo":{
            "class":"col-sm-6",
            "title":"Configuración General y de DB",
            "fields":{
                "id": fields_form["id"],
                "name": fields_form["name"],
                "label": fields_form["label"],
                "type": fields_form["type"],
                "helper": fields_form["helper"],
                "required": fields_form["required"],
                "readOnly": fields_form["readOnly"],
                "publicBlob": fields_form["publicBlob"],
                "default_value": fields_form["default_value"],
                }
            },
        "GeneralConfig":{
            "class":"col-sm-6",
            "title":"Config. del Formulario",
            "fields":{ 
                "sort": fields_form["sort"],
                "input": fields_form["input"],
                "select_options": fields_form["select_options"],
                "maxlength": fields_form["maxlength"],
                "extraclass": fields_form["extraclass"],
                "hidden": fields_form["hidden"],
                "calculate_file": fields_form["calculate_file"],
                "calculate_function": fields_form["calculate_function"],
            }
        },
        "ConnectedConfig":{
            "class":"col-sm-6",
            "title":"Config. de Conexiones",
            "fields":{
                "connected_table": fields_form["connected_table"],
                "clazz_id": fields_form["clazz_id"],
                "hasManyValues": fields_form["hasManyValues"]
            }
        }
    }
    return fields
def get_fields_form(parent=False):
    from utils.packages import application
    clazzes = application.getClazzDevelopList()
    options = [{"label": "Ninguna", "value": ""}] + [{"label": name, "value": id} for id, name in clazzes]
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
                    "label": "Nombre", 
                    "input": "text",
                    "class":""
                },
                "label": {
                    "id": "label", 
                    "type": "String", 
                    "maxlength": "100", 
                    "label": "Etiqueta", 
                    "input": "text",
                    "class":""
                },
                "type": {
                    "id": "type", 
                    "type": "String", 
                    "maxlength": "100", 
                    "label": "Tipo de Campo en BD", 
                    "input": "select",
                    "options": [
                        {"label": "String", "value": "String"},
                        {"label": "Integer", "value": "Integer"},
                        {"label": "Money", "value": "Money"},
                        {"label": "Boolean", "value": "Boolean"},
                        {"label": "Date", "value": "Date"},
                        {"label": "Time", "value": "Time"},
                        {"label": "DateTime", "value": "DateTime"},
			            {"label": "Text", "value": "Text"},
                        {"label": "Blob", "value": "blob"},
                        {"label": "Clase Foránea", "value": "connected_table"},
                        {"label": "Padre / hijo", "value": "selfParent"},
                        {"label": "Calculado (script)", "value": "calculate"},
                        {"label": "Creado por usuario", "value": "createdby"},
                        {"label": "Modificado por usuario", "value": "modifiedby"},
                        {"label": "Fecha Creación", "value": "creationDate"},
                        {"label": "Fecha Modificación", "value": "modificationDate"}
                    ],
                    "class":""
                },
                "helper": {
                    "id": "helper", 
                    "type": "String", 
                    "maxlength": "100", 
                    "label": "Helper para calculo", 
                    "input": "select",
                    "options": [
                        {"label": "", "value": ""},
                        {"label": "Script", "value": "script"},
                    ],
                    "class":""
                },
                "required": {
                    "id": "required", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Requerido", 
                    "input": "checkbox",
                    "class":""
                },
                "publicBlob": {
                    "id": "publicBlob", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Lectura Pública de archivos", 
                    "input": "checkbox",
                    "class":""
                },
                "default_value": {
                    "id": "default_value", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Default Value", 
                    "input": "textarea",
                    "class":""
                },
                "sort": {
                    "id": "sort", 
                    "type": "String", 
                    "maxlength": "100", 
                    "label": "Orden", 
                    "input": "text",
                    "class":""
                },
                "input": {
                    "id": "input", 
                    "type": "String", 
                    "maxlength": "100", 
                    "label": "Tipo de Campo en Formulario", 
                    "input": "select",
                    "options": [
                        {"label": "Texto", "value": "text"},
                        {"label": "Número", "value": "number"},
                        {"label": "Booleano", "value": "boolean"},
                        {"label": "Flotante", "value": "float"},
                        {"label": "Dinero", "value": "money"},
                        {"label": "Área de Texto", "value": "textarea"},
                        {"label": "Fecha", "value": "date"},
                        {"label": "Fecha Incompleta", "value": "incompletedate"},
                        {"label": "Imagen", "value": "image"},
                        {"label": "Blob", "value": "blob"},
                        {"label": "Teléfono", "value": "telephone"},
                        {"label": "Email", "value": "email"},
                        {"label": "Checkbox", "value": "checkbox"},
                        {"label": "Selector", "value": "select"},
                        {"label": "Radio", "value": "radius"},
                        {"label": "Foreing Class", "value": "connected_table"},
                        {"label": "Tags", "value": "tagsInput"},
                        {"label": "Vista Árbol", "value": "treeView"},
                    ],
                    "class":""
                },
                "select_options": {
                    "id": "select_options", 
                    "type": "Text", 
                    "maxlength": "", 
                    "label": "Opciones de Select", 
                    "input": "textarea",
                    "class":""
                },
                "maxlength": {
                    "id": "maxlength", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Extensión Máxima", 
                    "input": "number",
                    "class":""
                },
                "extraclass": {
                    "id": "extraclass", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Clases extra CSS", 
                    "input": "text",
                    "class":""
                },
                "hidden": {
                    "id": "hidden", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Ocultar", 
                    "input": "checkbox",
                    "class":""
                },
                "connected_table": {
                    "id": "connected_table", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Tabla Conectada", 
                    "input": "select",
                    "options": options,
                    "class":""
                },
                "clazz_id": {
                    "id": "clazz_id", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Id de la Clase", 
                    "input": "parent",
                    "value": parent or options,
                    "class":""
                },
                "readOnly": {
                    "id": "readOnly", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "Solo lectura", 
                    "input": "checkbox",
                    "class":""
                },
                "hasManyValues": {
                    "id": "hasManyValues", 
                    "type": "Boolean", 
                    "maxlength": "", 
                    "label": "¿Tiene múltiples valores?", 
                    "input": "checkbox",
                    "class":""
                },
                "calculate_file": {
                    "id": "calculate_file", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Archivo de Campos Calculados", 
                    "input": "text",
                    "class":""
                },
                "calculate_function": {
                    "id": "calculate_function", 
                    "type": "String", 
                    "maxlength": "255", 
                    "label": "Función de Campos Calculados", 
                    "input": "text",
                    "class":""
                },
            }
    return fields
