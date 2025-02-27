def listClazz():
    return list_class_names()

def list_class_names():
    from models.develop.clazz import Clazz
    allClasses = Clazz.query.all()
    class_names = [(clazz.id, clazz.name.lower()) for clazz in allClasses]
    return class_names

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','pdf','mp4','mp3','avi'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getClazzName(classid):
    return get_class_name(classid)

def get_class_name(classid):
    from models.develop.clazz import Clazz
    clazz = Clazz.query.get_or_404(classid)
    return clazz.name

def get_class_name_label(classid):
    from models.develop.clazz import Clazz
    clazz = Clazz.query.get_or_404(classid)
    return clazz.label

def getClazzFields(classname):
    from models.develop.clazz import Clazz
    clazz = Clazz.query.filter(Clazz.name == classname.capitalize()).first()
    return clazz.fields

def getClazzMoneyFields(classname):
    money_fields = {key.name for key in getClazzFields(classname) if key.type == 'Money'}
    return money_fields

def getClazzDateFields(classname):
    date_fields = {key.name for key in getClazzFields(classname) if key.type == 'Date'}
    return date_fields

def isPublic(fieldname, classname):
    from models.develop.clazz import Clazz
    from models.develop.field import Field
    
    # Buscar la clase por nombre
    clazz = Clazz.query.filter(Clazz.name == classname.capitalize()).first()
    if not clazz:
        return False  # Retorna False si la clase no se encuentra

    # Buscar el campo por nombre dentro de la clase
    field = Field.query.filter_by(clazz_id=clazz.id, name=fieldname).first()
    if not field:
        return False  # Retorna False si el campo no se encuentra
    
    return field.publicBlob

def getClazzDetails(value):
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
                print(f"{attr}: {value}")
    
    def getFields(self):
        return self.fields
    
class Clazz:
    def __init__(self, value):
        from models.develop.clazz import Clazz
        
        # Verificar si 'value' es una cadena
        if isinstance(value, str):
            # Buscar por nombre (se asume que el nombre está capitalizado)
            clazz = Clazz.query.filter(Clazz.name == value.capitalize()).first()
        else:
            # Asumir que 'value' es un entero y buscar por ID
            clazz = Clazz.query.get_or_404(value)
        
        # Copiar los atributos del objeto consultado a la instancia actual
        if clazz:
            for attr in dir(clazz):
                if not attr.startswith("_") and hasattr(clazz, attr):
                    setattr(self, attr, getattr(clazz, attr))

    def getName(self):
        return getattr(self, "name")

    def getId(self):
        return getattr(self, "id")

    def getLabel(self):
        return getattr(self, "label")
    
    def getSearchFields(self):
        return getattr(self, "search_fields")

    def displaySearchFields(self,searchFields):
        fields = self.getFields()
        fieldDict = {}
        
        print(fields)
        print(searchFields)
        if "id" in searchFields:
            fieldDict["# Orden"] = {
                    "name": "id",
                    "input": "integer"
                }
        for field in fields:
            if field.name in searchFields:
                print(field.name)
                print(field.input)
                print(field.type)
                if field.input == "select":
                    fieldOptions = field.select_options
                    options = {}
                    if fieldOptions and ',' in fieldOptions and '|' in fieldOptions:
                        for option in fieldOptions.split(","):
                            options[option.split("|")[0]] = option.split("|")[1]
                    fieldDict[field.label] = {
                        "name": field.name,
                        "input": field.input,
                        "options": options
                    }
                else:
                    fieldDict[field.label] = {
                        "name": field.name,
                        "input": field.input
                    }
        
        return fieldDict

    def getDisplayFields(self):
        return getattr(self, "table_fields")
    
    def getPlural(self):
        return getattr(self, "plural")

    def getSortField(self):
        return getattr(self, "sort_field_results")
    
    def getRepresentation(self):
        if hasattr(self, "clazz_representation"):
            return getattr(self, "clazz_representation")
        else:
            return False 

    def getFields(self):
        return self.fields
    
    def getContainers(self):
        return self.containers
    
    def getRelevants(self):
        return self.relevants
    
