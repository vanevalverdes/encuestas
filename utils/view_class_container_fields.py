from sqlalchemy.orm import joinedload
from models.develop.clazz import Clazz
from models.develop.container import Container
from models.develop.field import Field 
from utils.methods import session, application

def get_clazz_fields(clazz_id):
    # Usar joinedload para cargar anticipadamente las relaciones
    clazz = Clazz.query.options(
        joinedload(Clazz.containers).joinedload(Container.fields)
    ).get(clazz_id)

    if not clazz:
        return None

    fields = {}
    for container in clazz.containers:
        container_fields = {}
        
        fieldsUnsorted = container.fields
        fieldsSorted = session.sortTableBy(fieldsUnsorted, "sort")
        for field in fieldsSorted:
            if field.input == "connected_table":
                all = session.getTable(application.get_class_name(field.connected_table)).all()
                options = {}
                options[""] = ""
                for item in all:
                    options[item.__repr__()] = item.id
            else:
                fieldOptions = field.select_options
                options = {}
                if fieldOptions and ',' in fieldOptions and '|' in fieldOptions:
                    for option in fieldOptions.split(","):
                        options[option.split("|")[0]] = option.split("|")[1]
            
            defaultValue = ""
            if field.default_value != None:
                if field.default_value.strip() == "random()":
                    from utils.methods.engine import random
                    defaultValue = random()
                    print(defaultValue)
                elif field.default_value.strip() == "now()":
                    from datetime import datetime, timezone 
                    defaultValue = datetime.now(timezone.utc)
                else:
                    defaultValue = field.default_value
                print(field.default_value )
               
            container_fields[field.name] = {
                "id": field.name,
                "type": field.type,
                "maxlength": field.maxlength or "",
                "label": field.label,
                "input": field.input,
                "class": field.extraclass or "",
                "select_options": options or "",
                "connected_table": field.connected_table or "",
                "required": field.required or "",
                "hidden": field.hidden or "",
                "defaultValue": defaultValue or ""
            }
        fields[container.name] = {
            "type": container.type,
            "class": container.extraclass or "col-sm-12",
            "title": container.title,
            "connected_table": container.connected_table or "",
            "connected_table_fields": container.connected_table_fields or "",
            "fields": container_fields
        }
    return fields

def get_clazz_fields_migration(clazz_id):
    # Usar joinedload para cargar anticipadamente las relaciones
    clazz = Clazz.query.options(
        joinedload(Clazz.containers).joinedload(Container.fields)
    ).get(clazz_id)

    if not clazz:
        return []

    field_list = []
    for container in clazz.containers:
        for field in container.fields:
            field_dict = {
                "name": field.name,
                "type": field.type,
                "connected_table": field.connected_table,
                "maxlength": field.maxlength or None  # Usamos None para indicar que no hay un valor específico de maxlength
            }
            field_list.append(field_dict)

    return field_list
