from sqlalchemy.orm import joinedload
from models.develop.clazz import Clazz
from models.develop.container import Container
from models.develop.field import Field 
from utils.packages import session, application

def get_clazz_fields_db(clazz_id):
    from models.develop.clazz import Clazz
    if isinstance(clazz_id, int):
        clazz = Clazz.query.get(clazz_id)
    elif isinstance(clazz_id, str):
        clazz = Clazz.query.filter(Clazz.name == clazz_id.capitalize()).first()

    if not clazz:
        return None

    fields = {}
    for field in clazz.fields:
        defaultValue = ""
        if field.default_value != None:
            if field.default_value.strip() == "random()":
                from utils.packages.engine import random
                defaultValue = random()
            elif field.default_value.strip() == "now()":
                from datetime import datetime, timezone 
                defaultValue = datetime.now(timezone.utc)
            else:
                defaultValue = field.default_value

        readOnly = False
        if field.type == "calculate" or field.readOnly == True:
            readOnly = True

        fields[field.name] = {
            "id": field.name,
            "type": field.type,
            "name": field.name,
            "label": field.label,
            "sort": field.sort,
            "publicBlob": field.publicBlob or False,
            "input": field.input,
            "extraclass": field.extraclass or "",
            "maxlength": field.maxlength or None, 
            "select_options": field.select_options or "",
            "required": field.required or False,
            "hidden": field.hidden or False,
            "readOnly": readOnly,
            "hasManyValues": field.hasManyValues or False,
            "connected_table": field.connected_table or "",
            "defaultValue": defaultValue,
            "calculate_file": field.calculate_file,
            "calculate_function": field.calculate_function,
            "helper": field.helper,
        }
    return fields

def get_clazz_fields(clazz_id):
    fieldsList = application.getClazz(clazz_id).getFields()

    fields = {}
    fields["id"] = {
        "id": "id",
        "type": "Integer",
        "name": "id",
        "label": "Id",
        "sort": None,
        "publicBlob": False,
        "input": "integer",
        "extraclass": None,
        "maxlength": None, 
        "select_options": None,
        "required": False,
        "hidden": False,
        "readOnly": True,
        "hasManyValues": False,
        "connected_table": None,
        "defaultValue": None,
        "calculate_file": None,
        "calculate_function": None,
    }
    for field_name, field in fieldsList.items():
        defaultValue = ""
        if field.get("default_value") != None:
            if field.get("default_value").strip() == "random()":
                from utils.packages.engine import random
                defaultValue = random()
            elif field.get("default_value").strip() == "now()":
                from datetime import datetime, timezone 
                defaultValue = datetime.now(timezone.utc)
            else:
                defaultValue = field.get("default_value")

        readOnly = False
        if field.get("type") == "calculate" or field.get("readOnly") == True:
            readOnly = True

        fields[field.get("name")] = {
            "id": field.get("name"),
            "type": field.get("type"),
            "name": field.get("name"),
            "label": field.get("label"),
            "sort": field.get("sort"),
            "publicBlob": field.get("publicBlob") or False,
            "input": field.get("input"),
            "extraclass": field.get("extraclass") or "",
            "maxlength": field.get("maxlength") or None,
            "select_options": field.get("select_options") or "",
            "required": field.get("required") or False,
            "hidden": field.get("hidden") or False,
            "readOnly": readOnly,
            "hasManyValues": field.get("hasManyValues") or False,
            "connected_table": field.get("connected_table") or "",
            "defaultValue": defaultValue,
            "calculate_file": field.get("calculate_file"),
            "calculate_function": field.get("calculate_function"),
            "helper": field.get("helper"),
        }
    return fields

def get_clazz_fields_migration(clazz_id):
    from models.develop.clazz import Clazz
    if isinstance(clazz_id, int):
        clazz = Clazz.query.get(clazz_id)
    elif isinstance(clazz_id, str):
        clazz = Clazz.query.filter(Clazz.name == clazz_id.capitalize()).first()

    if not clazz:
        return None
    
    fields = {}
    for field in clazz.fields:
        fields[field.name] = {
            "id": int(field.id),
            "type": field.type,
            "name": field.name,
            "maxlength": int(field.maxlength) if field.maxlength else None,
            "connected_table": int(field.connected_table) if field.connected_table else None,
            "label": field.label,
            "input": field.input,
            "sort": field.sort,
            "required": field.required if field.required else False,
            "hidden": field.hidden if field.hidden else False,
            "publicBlob": field.publicBlob if field.publicBlob else False,
            "default_value": f"{field.default_value}" if field.default_value else None,
            "select_options": field.select_options,
            "extraclass": field.extraclass,
            "hasManyValues": field.hasManyValues if field.hasManyValues else False,
            "readOnly": field.readOnly if field.readOnly else False,
            "calculate_file": field.calculate_file,
            "calculate_function": field.calculate_function,
            "helper": field.helper,
        }
    return fields

def get_clazz_relevants_migration(clazz_id):
    from models.develop.clazz import Clazz
    if isinstance(clazz_id, int):
        clazz = Clazz.query.get(clazz_id)
    elif isinstance(clazz_id, str):
        clazz = Clazz.query.filter(Clazz.name == clazz_id.capitalize()).first()

    if not clazz:
        return None
    
    fields = {}
    for field in clazz.relevants:
        fields[field.id] = {
            "id": int(field.id),
            "search": field.search if field.search else False,
            "create": field.create if field.create else False,
            "edit": field.edit if field.edit else False,
            "delete": field.delete if field.delete else False,
            "read": field.read if field.read else False,
            "usergroup_id": int(field.usergroup_id) if field.usergroup_id else None,
        }
    return fields
