from utils.db import db

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
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'))
    container = db.relationship('Container', order_by="Field.sort.asc()", backref='fields')
    clazz_id = db.Column(db.Integer, db.ForeignKey('clazz.id'))
    clazz = db.relationship('Clazz', order_by="Field.sort.asc()", backref='fields')

    def __repr__(self) -> str:
        return f"{self.name}"

def get_fields(parent=False):
    from utils.methods import application
    clazzes = application.list_class_names()
    options = [{"label": "Ninguna", "value": ""}] + [{"label": name, "value": id} for id, name in clazzes]
    if parent:
        container = application.getContainerDetails(parent)
        print(parent)
        clazzparent = container.getClazz()
        print(clazzparent)
    fields = {
        "GeneralInfo":{
            "class":"col-sm-6",
            "title":"Configuración General y de DB",
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
                        {"label": "Foreing Class", "value": "connected_table"},
                        {"label": "Creado por usuario", "value": "createdby"},
                        {"label": "Modificado por usuario", "value": "modifiedby"},
                        {"label": "Fecha Creación", "value": "creationDate"},
                        {"label": "Fecha Modificación", "value": "modificationDate"}
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
            }
        },
        "GeneralConfig":{
            "class":"col-sm-6",
            "title":"Config. del Formulario",
            "fields":{
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
                        {"label": "Flotante", "value": "float"},
                        {"label": "Área de Texto", "value": "textarea"},
                        {"label": "Fecha", "value": "date"},
                        {"label": "Blob", "value": "blob"},
                        {"label": "Teléfono", "value": "telephone"},
                        {"label": "Email", "value": "email"},
                        {"label": "Checkbox", "value": "checkbox"},
                        {"label": "Selector", "value": "select"},
                        {"label": "Radio", "value": "radius"},
                        {"label": "Foreing Class", "value": "connected_table"},
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
                }
            }
        },
        "ConnectedConfig":{
            "class":"col-sm-6",
            "title":"Config. de Conexiones",
            "fields":{
                "connected_table": {
                    "id": "connected_table", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Tabla Conectada", 
                    "input": "select",
                    "options": options,
                    "class":""
                },
                "container_id": {
                    "id": "container_id", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Id del Container al que pertenece", 
                    "input": "parent",
                    "value": parent or "",
                    "class":""
                },
                "clazz_id": {
                    "id": "clazz_id", 
                    "type": "Integer", 
                    "maxlength": "", 
                    "label": "Id de la Clase", 
                    "input": "parent",
                    "value": clazzparent or options,
                    "class":""
                }
            }
        }
    }
    return fields
