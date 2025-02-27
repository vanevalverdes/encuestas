def translation(page):    
    records = getRecord('Translate', page).getConnectedTable("TranslateField")
    translation = {}
    for record in records:
        item = {
            "ES": record.valueES,
            "EN": record.valueEN
        }
        translation[record.name] = item
    return translation

def getClazz(classname):
    # Importar dinámicamente la clase correcta
    module_path = f'models.production.{classname.lower()}'
    model_module = __import__(module_path, fromlist=[classname.lower()])
    modelClass = getattr(model_module, classname.capitalize())
    return modelClass

def saveForm(institution, containers, id=None):
    from utils.db import db
    from . import application
    from werkzeug.utils import secure_filename
    import os
    from flask import request, current_app
    from datetime import datetime
    from . import engine
    import uuid
    
    # Define los diferentes tipos de campos
    checkbox_fields_boolean = {key for container_key, container in containers.items()
                for key, value in container['fields'].items() if value['input'] == 'checkbox' and value['type'] == 'Boolean'}
    checkbox_fields = {key for container_key, container in containers.items()
                for key, value in container['fields'].items() if value['input'] == 'checkbox' and value['type'] != 'Boolean'}
    integer_fields = {key for container_key, container in containers.items()
            for key, value in container['fields'].items() if value['input'] == 'Integer'}
    money_fields = {key for container_key, container in containers.items()
            for key, value in container['fields'].items() if value['type'] == 'Money'}
    date_fields = {key for container_key, container in containers.items()
            for key, value in container['fields'].items() if value['input'] == 'date'}
    blob_fields = {key for container_key, container in containers.items()
            for key, value in container['fields'].items() if value['input'] == 'blob'}
    
    # Itera sobre los campos del formulario que coinciden con los nombres de las columnas
    for key in request.form:
        if hasattr(institution, key):
            if key in checkbox_fields_boolean:
                setattr(institution, key, request.form[key] == 'on')
            elif key in integer_fields:
                setattr(institution, key, int(request.form[key]))
            elif key in money_fields and request.form[key] != '':
                val = float(request.form[key])
                val = engine.floatToMoney(val)
                setattr(institution, key, val.getCents())
            elif key in date_fields:
                setattr(institution, key, datetime.strptime(request.form[key], '%Y-%m-%d').date())
            elif key in checkbox_fields:
                checks = request.form.getlist(key)
                setattr(institution, key, str(checks))
            else:
                value = request.form[key]
                setattr(institution, key, None if value == '' else value)

    # Asegura que los checkboxes no marcados se actualicen como False
    for field in checkbox_fields_boolean:
        if field not in request.form:
            setattr(institution, field, False)
    for field in checkbox_fields:
        if field not in request.form:
            setattr(institution, field, False)
    
    # Función para guardar los blobs
    def saveBlobs(blob_folder):
        # Verifica si la carpeta existe; si no, la crea
        if not os.path.exists(blob_folder):
            os.makedirs(blob_folder)
        # Manejo del archivo de imagen
        for key in request.files:
            file = request.files[key]
            if file.filename != '':
                if file and application.allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    if key in blob_fields:
                        file.save(os.path.join(blob_folder, filename))
                    setattr(institution, key, filename)
            else:
                setattr(institution, key, None)

    # Lógica para manejar nuevos y existentes registros
    if not id:
        if blob_fields:
            db.session.add(institution)
            db.session.commit()
            id = institution.id
            blob_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(id))
            saveBlobs(blob_folder)
            db.session.commit()
        else:
            db.session.add(institution)
            db.session.commit()
    else:
        blob_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(id))
        saveBlobs(blob_folder)
        db.session.commit()

def printLocals(variables):    
    for var_name, value in variables.items():
        print(f'{var_name}: {value}')

def groupBy(records, fieldname):
    from itertools import groupby
    from operator import attrgetter

    # Ordenar los registros por el campo especificado
    records_sorted = sorted(records, key=attrgetter(fieldname))
    # Agrupar los registros por el campo especificado
    grouped_records = {
        str(key): list(group)  # Convertir key a string
        for key, group in groupby(records_sorted, key=lambda x: str(getattr(x, fieldname)))
    }
    return grouped_records

def getTable(classname):
    tableRecord = table(classname)
    return tableRecord

def classQuery(classname, columns, filterstring):
    columns = "Products.name, Products.id"
    # result = table(classname) \
    #         .with_entities(columns) \
    #         .getAllRecords()
    # return result

def getRecord(classname, record_id):
    # Crear y devolver una instancia de la clase `Record`
    return Record(classname, record_id)

def getORMRecord(classname, record_id):
    # Crear y devolver una instancia de la clase `Record`
    module_path = f'models.production.{classname.lower()}'
    model_module = __import__(module_path, fromlist=[classname.lower()])
    modelClass = getattr(model_module, classname.capitalize())

    # Obtener el registro de la base de datos
    return modelClass.query.get_or_404(record_id)

def sortTableBy(table, fieldname):
    from operator import attrgetter

    def none_safe_key(value):
        # Usa attrgetter para obtener el valor del campo
        field_value = attrgetter(fieldname)(value)
        return (field_value is None, field_value)

    fieldsSorted = sorted(table, key=none_safe_key)
    return fieldsSorted

def filterTableView(classname):
    from flask import request
    try:
        query = newQuery(classname)
        for key in request.args:
            if request.args[key]:  
                if key.startswith("start-"):
                    name = key.split('-')[1]
                    query.addFilter(name, ">=", request.args[key])
                elif key.startswith("until-"):
                    name = key.split("-")[1]
                    query.addFilter(name, "<=", request.args[key])
                elif key.startswith("str-"):
                    name = key.split("-")[1]
                    query.addFilter(name, "like", request.args[key])
                elif key == "createdBy":
                        query.addFilter("createdby_id", "==", request.args[key])
                else:
                    query.addFilter(key, "==", request.args[key])
        #table = query.getTable()
        return query
    except Exception as e:
        print(f"Error al filtrar la tabla: {e}")
        return None

def putVariable(variable,value):
    from flask import session
    session[variable] = value
    return True
def getVariable(variable):
    from flask import session
    return session.get(variable)

def newQuery(classname):
    return Query(classname)

class Query:
    def __init__(self, classname):
        # Importar dinámicamente la clase correcta
        module_path = f'models.production.{classname.lower()}'
        model_module = __import__(module_path, fromlist=[classname.capitalize()])
        modelClass = getattr(model_module, classname.capitalize())
        self.model_class = modelClass
        self.query = modelClass.query
    
    def set(self):
        return self.model_class
    
    def addFilter(self, fieldname, operator, value):
        # Definir un diccionario de operadores
        operators = {
            "==": lambda f, v: f == v,
            "!=": lambda f, v: f != v,
            "<": lambda f, v: f < v,
            ">": lambda f, v: f > v,
            "<=": lambda f, v: f <= v,
            ">=": lambda f, v: f >= v,
            "like": lambda f, v: f.ilike(f"%{v}%")
        }

        # Obtener la función del operador adecuado
        op_func = operators.get(operator)

        if op_func is None:
            raise ValueError(f"Operador no soportado: {operator}")

        # Filtrar por el campo utilizando la función del operador
        self.query = self.query.filter(op_func(getattr(self.model_class, fieldname), value))
        return self
    
    def getTableQuery(self):
        return self.query
    
    def getTable(self):
        return self.query.all()
    
    def pagination(self, page, per_page=50):
        paginated = self.query.paginate(page=page, per_page=per_page, error_out=False)
        return paginated
    
    def sortBy(self, fieldname, direction='asc'):
        from sqlalchemy import asc, desc
        field = getattr(self.model_class, fieldname)
        if direction == 'asc':
            self.query = self.query.order_by(asc(field))
        elif direction == 'desc':
            self.query = self.query.order_by(desc(field))
        else:
            raise ValueError("direction must be 'asc' or 'desc'")
        return self
    
    def groupBy(self, fieldname):
        from itertools import groupby
        from operator import attrgetter

        # Obtener todos los registros
        records = self.getTable()
        # Ordenar los registros por el campo especificado
        records_sorted = sorted(records, key=attrgetter(fieldname))
        # Agrupar los registros por el campo especificado
        grouped_records = {
            str(key): list(group)  # Convertir key a string
            for key, group in groupby(records_sorted, key=lambda x: str(getattr(x, fieldname)))
        }
        return grouped_records
    
    def count(self):
        return self.query.count()
    
class table:
    def __init__(self, classname):
        # Importar dinámicamente la clase correcta
        module_path = f'models.production.{classname.lower()}'
        model_module = __import__(module_path, fromlist=[classname.lower()])
        modelClass = getattr(model_module, classname.capitalize())
        self.model_class = modelClass
    
    def set(self):
        return self.model_class
           
    def getFilteredTable(self, fieldname, operator, value):
        # Obtener la clase de la instancia
        clazz = self.model_class

        # Definir un diccionario de operadores
        operators = {
            "==": lambda f, v: f == v,
            "!=": lambda f, v: f != v,
            "<": lambda f, v: f < v,
            ">": lambda f, v: f > v,
            "<=": lambda f, v: f <= v,
            ">=": lambda f, v: f >= v
        }

        # Obtener la función del operador adecuado
        op_func = operators.get(operator)

        if op_func is None:
            raise ValueError(f"Operador no soportado: {operator}")

        # Filtrar por el campo utilizando la función del operador
        filtered_records = clazz.query.filter(op_func(getattr(clazz, fieldname), value)).all()
        return filtered_records
    
    def groupBy(self, fieldname):
        from itertools import groupby
        from operator import attrgetter

        # Obtener todos los registros
        records = self.all()
        # Ordenar los registros por el campo especificado
        records_sorted = sorted(records, key=attrgetter(fieldname))
        # Agrupar los registros por el campo especificado
        grouped_records = {
            str(key): list(group)  # Convertir key a string
            for key, group in groupby(records_sorted, key=lambda x: str(getattr(x, fieldname)))
        }
        return grouped_records
    
    def getFirstRecord(self):
        # Obtener la clase de la instancia
        clazz = self.model_class
        # Obtener el primer registro
        first_record = clazz.query.first()
        if first_record:
            # Crear una instancia de la clase `record`
            record_instance = Record(clazz.__name__, first_record.id)
            return record_instance
        return None
    
    def getAllRecords(self):
        # Obtener todos los registros de la tabla
        return self.model_class.query.all()
    
    def all(self, sort='asc'):
        """
        Obtiene todos los registros de la tabla y los ordena según el valor de 'sort'.
        
        :param sort: 'asc' para ordenar en orden ascendente (por defecto), 'desc' para ordenar en orden descendente.
        :return: Lista de registros ordenados.
        """
        # Obtener todos los registros de la tabla
        table = self.model_class.query.all()
        if sort == 'desc':
            # Ordenar los registros en orden descendente por 'id'
            records_sorted = sorted(table, key=lambda x: x.id, reverse=True)
        else:
            # Ordenar los registros en orden ascendente por 'id'
            records_sorted = sorted(table, key=lambda x: x.id)
        return records_sorted
    
    def getEmptyTable(self):
        # Crear una instancia vacía de la clase
        return self.model_class()

class Record:
    def __init__(self, classname, record_id):
        # Importar dinámicamente la clase correcta
        module_path = f'models.production.{classname.lower()}'
        model_module = __import__(module_path, fromlist=[classname.capitalize()])
        modelClass = getattr(model_module, classname.capitalize())

        # Obtener el registro de la base de datos
        record = modelClass.query.get_or_404(record_id)
        self.record = record
        # Copiar los atributos del objeto consultado a la instancia actual
        #if record_instance:
        #    for attr in dir(record_instance):
        #        if not attr.startswith("_") and hasattr(record_instance, attr):
        #            setattr(self, attr, getattr(record_instance, attr))
        
    def set(self):
        return self.record
    
    def store(self, label, value):
        if hasattr(self.record, label):
            setattr(self.record, label, value)
            from utils.db import db
            db.session.commit()  # Asegúrate de usar db.session.commit() para confirmar los cambios
            return True
        return False

    def getConnectedTable(self, tableName):
        from models.develop.clazz import Clazz
        # Obtener la clase Clazz por nombre
        clazz = Clazz.query.filter_by(name=tableName.capitalize()).first()
        if clazz is None:
            raise AttributeError(f"No class named '{tableName}' found.")
        
        # Obtener el nombre plural de la tabla conectada
        connected_table_name = clazz.plural
        
        # Obtener los registros conectados
        connected_records = getattr(self.record, connected_table_name, None)
        if connected_records is not None:
            return connected_records
        else:
            raise AttributeError(f"No connected table named '{tableName}' found for the record.")

    def get(self, label):
        # Acceder al atributo del registro
        return getattr(self.record, label, None)

    def set(self):
        return self.record

class newRecord():
    def __init__(self, classname):
        clazz = getClazz(classname)
        record = clazz()
        self.record = record
    
    def store(self, label, value):
        return setattr(self.record, label, value)
    
    def save(self):
        from utils.db import db
        db.session.add(self.record)
        db.session.commit()
        return self.record
    
    def get(self, label):
        # Acceder al atributo del registro
        return getattr(self.record, label, None)