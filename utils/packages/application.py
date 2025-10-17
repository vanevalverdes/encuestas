def createClazzRecord(name,label=None,tag=None,plural=None,sort_field_results=None,table_fields=None,search_fields=None,clazz_representation=None):
    from models.develop.clazz import Clazz
    clazz = Clazz(
        name=name.capitalize(),
        label=label,
        tag=tag,
        plural=plural,
        sort_field_results=sort_field_results,
        table_fields=table_fields,
        search_fields=search_fields,
        clazz_representation=clazz_representation
    )
    from utils.db import db
    db.session.add(clazz)
    db.session.commit()
    return clazz

def createContainerRecord(name,title=None,extraclass=None,type=None,connected_table=None,connected_table_fields=None,clazz_id=None):
    from models.develop.container import Container
    container = Container(
        name=name,
        title=title,
        extraclass=extraclass,
        type=type,
        connected_table=connected_table,
        connected_table_fields=connected_table_fields,
        clazz_id=clazz_id
    )
    from utils.db import db
    db.session.add(container)
    db.session.commit()
    return container

def createFieldRecord(fieldname,clazz_id,field_type,field_label=None,field_input=None,select_options=None,publicBlob=False,maxlength=None,connected_table=None,sort=None,required=False,hidden=False,default_value=None,extraclass=None,container_id=None):
    from models.develop.field import Field
    from utils.db import db
    field = Field(
        name=fieldname,
        clazz_id=clazz_id,
        type=field_type,
        label=field_label if field_label else fieldname.capitalize(),
        input=field_input,
        select_options=select_options,
        publicBlob=publicBlob,
        maxlength=maxlength,
        connected_table=connected_table,
        sort=sort,
        required=required,
        hidden=hidden,
        default_value=default_value,
        extraclass=extraclass
    )
    db.session.add(field)
    db.session.commit()
    return field

def import_clazz(dict):
    def safe_int(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None
    def safe_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().lower() in ("true", "1", "yes", "si")
        return bool(val)
    # Crear la clase principal
    newClazz = createClazzRecord(
        name=dict['name'],
        label=dict['label'],
        tag=dict.get('tag', ''),
        plural=dict['plural'],
        sort_field_results=dict.get('sort_field_results', ''),
        table_fields=dict.get('table_fields', ''),
        search_fields=dict.get('search_fields', ''),
        clazz_representation=dict.get('clazz_representation', '')
    )
    # Crear los contenedores y campos
    for container_name, container_data in dict["containers"].items():
        container = createContainerRecord(
            name=container_name,
            title=container_data.get('title', None),
            extraclass=container_data.get('class', ''),
            type=container_data.get('type', ''),
            connected_table=safe_int(container_data.get('connected_table', 0)),
            connected_table_fields=container_data.get('connected_table_fields', ''),
            clazz_id=newClazz.id
        )
        for field_name, field_data in container_data['fields'].items():
            createFieldRecord(
                fieldname=field_name,
                clazz_id=safe_int(newClazz.id),
                field_type=field_data.get('type', ''),
                field_label=field_data.get('label', ''),
                field_input=field_data.get('input', ''),
                select_options=field_data.get('select_options', None),
                publicBlob=False,
                maxlength=safe_int(field_data.get('maxlength', 0)),
                connected_table=safe_int(field_data.get('connected_table', 0)),
                sort=None,
                required=safe_bool(field_data.get('required', False)),
                hidden=safe_bool(field_data.get('hidden', False)),
                default_value=field_data.get('defaultValue', None),
                extraclass=field_data.get('class', None),
            )
    print(f"Created new class: {newClazz.name}")
    return True

def listClazz():
    return list_class_names()

def list_class_names():
    from models.production import clazzlist
    allClasses = clazzlist.get_list_by_name().values()
    class_names = [(clazz['id'], clazz['name'].lower()) for clazz in allClasses]
    return class_names

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','pdf','mp4','mp3','avi'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getClazzDevelop(classid):
    from models.develop.clazz import Clazz
    if isinstance(classid, int):
        clazz = Clazz.query.get(classid)
    elif isinstance(classid, str):
        clazz = Clazz.query.filter(Clazz.name == classid.capitalize()).first()
    return clazz

def getClazzDevelopList():
    from models.develop.clazz import Clazz
    clazzes = Clazz.query.all()
    class_names = [(clazz.id, clazz.name.lower()) for clazz in clazzes]
    return class_names

def getClazzName(classid):
    return get_class_name(classid)

def get_template(classname):
    # Buscar la clase por nombre
    clazz = Clazz(classname)
    if not clazz:
        return False
    return clazz.getTemplate()

def getFieldTreeView(classname):
    # Buscar la clase por nombre
    clazz = Clazz(classname)
    if not clazz:
        return False
    return clazz.getTreeView()

def get_class_name(classid):
    # Buscar la clase por nombre
    clazz = Clazz(classid)
    if not clazz:
        return False  # Retorna False si la clase no se encuentra
    return clazz.getName()

def get_class_name_label(classid):
    # Buscar la clase por nombre
    clazz = Clazz(classid)
    if not clazz:
        return False  # Retorna False si la clase no se encuentra
    return clazz.getLabel()

def getClazzFields(classname):
    # Buscar la clase por nombre
    clazz = Clazz(classname)
    if not clazz:
        return False  # Retorna False si la clase no se encuentra
    fields = clazz.getFields()
    if not fields:
        return False  # Retorna False si no hay campos
    return fields

def isPublic(fieldname, classname):
    # Buscar la clase por nombre
    clazz = Clazz(classname)
    if not clazz:
        return False  # Retorna False si la clase no se encuentra
    fields = clazz.getFields()
    # Buscar el campo por nombre dentro de la clase
    field = fields.get(fieldname).get("publicBlob")
    return field

def getClazzDetails(value):
    return Clazz(value).getDetails()

def getClazz(value):
    return Clazz(value)

def getContainerDetails(value):
    return Container(value)

def getAllClazzes():
    from models.develop.clazz import Clazz
    return Clazz.query.all()

def getAllUsergroups():
    from models.develop.usergroup import Usergroup
    return Usergroup.query.all()

def getMenu(usergroup):
    from models.production.menu import Menu
    import json

    try:
        record = Menu.query.filter(Menu.usergroup == usergroup).first()
        if record:
            menu = json.loads(record.menulist)
            #menu = {}
            #for line in menu_list.split(","):
            #    parts = line.split("|")
            #    if len(parts) == 2:
            #        menu[parts[0]] = parts[1]
            #    else:
            #        raise ValueError(f"Invalid format in menulist: {line}")
            return menu
        else:
            return None  # o alguna respuesta adecuada cuando no hay registro
    except Exception as e:
        print(f"Error while fetching menu: {e}")
        #if usergroup == 1:
        #    menu = {}
        #    menu["Configurations"] = "/admin/configs/"
        #return menu
    
class Container:
    def __init__(self, value):   
        # Importar dinámicamente la clase correcta
        module_path = f'models.develop.container'
        model_module = __import__(module_path, fromlist=["Container"])
        modelClass = getattr(model_module, "Container")

        # Obtener el registro de la base de datos
        record_instance = modelClass.query.get_or_404(value)

        # Copiar los atributos del objeto consultado a la instancia actual
        if record_instance:
            for attr in dir(record_instance):
                if not attr.startswith("_") and hasattr(record_instance, attr):
                    setattr(self, attr, getattr(record_instance, attr))

    def getName(self):
        return getattr(self, "name")
    
    def getId(self):
        return getattr(self, "id")

    def getClazz(self):
        return getattr(self, "clazz_id")
    
    def getAttr(self):
        for attr in dir(self):
            if not attr.startswith("_"):  # Omitir atributos y métodos privados
                value = getattr(self, attr)
                #print(f"{attr}: {value}")
    
    def getFields(self):
        return self.fields
    
class Clazz:
    def __init__(self, value):    
        from models.production import clazzlist
        import importlib
        if isinstance(value, int):
            class_info = clazzlist.get_list_by_id().get(value)
        elif isinstance(value, str):
            class_info = clazzlist.get_list_by_name().get(value.lower())
        else:
            raise TypeError("clazz_id debe ser un entero (ID) o una cadena (nombre).")

        if not class_info:
            raise ValueError(f"Clase con ID/Nombre '{value}' no encontrada.")
        
        name = class_info.get("name").lower()
        route_module_name = f"models.production.{name}"
        
        try:
            route_module = importlib.import_module(route_module_name)
        except ImportError:
            raise ImportError(f"No se pudo importar el módulo: {route_module_name}")
        
        self.model = route_module
        self.details = class_info

    def getDetails(self):
        return self.details

    def getName(self):
        return self.details.get("name")

    def getId(self):
        return self.details.get("id")

    def getTemplate(self):
        return self.details.get("template")

    def getTreeView(self):
        return self.details.get("treeView")

    def getLabel(self):
        return self.details.get("label")
    
    def getSearchFields(self):
        return [field.strip() for field in self.details.get("search_fields").split(",")]

    def displaySearchFields(self):
        searchFields = self.getSearchFields()
        fields = self.getFields()
        fieldDict = {}
        
        #print(fields)
        #print(searchFields)
        if "id" in searchFields:
            fieldDict["# ID"] = {
                    "name": "id",
                    "input": "integer"
                }
        for field in fields.values():
            if field.get("name") in searchFields:
                #print(field.name)
                #print(field.input)
                #print(field.type)
                if field.get("input") == "select":
                    fieldOptions = field.get("select_options")
                    options = {}
                    if fieldOptions and ',' in fieldOptions and '|' in fieldOptions:
                        for option in fieldOptions.split(","):
                            options[option.split("|")[0]] = option.split("|")[1]
                    fieldDict[field.get("label")] = {
                        "name": field.get("name"),
                        "input": field.get("input"),
                        "options": options
                    }
                else:
                    fieldDict[field.get("label")] = {
                        "name": field.get("name"),
                        "input": field.get("input")
                    }
        
        return fieldDict

    def getDisplayFields(self):
        return self.details.get("table_fields")
    
    def getTableFields(self):
        return self.details.get("table_fields")
    
    def getPlural(self):
        return self.details.get("plural")

    def getSortField(self):
        return self.details.get("sort_field_results")
    
    def getRepresentation(self):
        if self.details.get("clazz_representation"):
            return self.details.get("clazz_representation")
        else:
            return False 

    def getFields(self):
        if hasattr(self.model, 'get_fields'):
            fieldsList = self.model.get_fields()
        else:
            raise AttributeError(f"La función 'get_fields' no se encontró en el módulo: {self.details.get('filename')}")
        if not fieldsList:
            return None
        return fieldsList
    
    def getContainers(self):
        return self.containers
    
    def getRelevants(self):
        if hasattr(self.model, 'get_relevants'):
            relevants = self.model.get_relevants()
        else:
            raise AttributeError(f"La función 'get_relevants' no se encontró en el módulo: {self.details.get('filename')}")
        if not relevants:
            return None
        return relevants
    
