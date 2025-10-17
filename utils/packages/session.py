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

def updateHistory(pop_index=None):
    """
    Función auxiliar: Añade la URL actual al historial de sesión.
    
    Args:
        pop_index (int | None): Si se proporciona un índice (ej: -2 o -3), 
                                 el elemento en ese índice se elimina ANTES 
                                 de añadir la URL actual.
    """

    # Configuración básica para limitar el tamaño del historial
    MAX_HISTORY = 10
    
    from flask import session, request
    
    current_url = request.url

    if 'history' not in session:
        session['history'] = []
        
    history = session.get('history', [])

    if pop_index is not None:
        try:
            history.pop(pop_index) 
        except IndexError:
            pass
            
    # Verificar la longitud antes de acceder a history[-2]
    if len(history) >= 2 and current_url and (current_url == history[-2]):
        history.pop(-1)
        
    if not history or history[-1] != current_url:
        history.append(current_url)

        if len(history) > MAX_HISTORY:
            history.pop(0) 

    session['history'] = history

def getBackUrl(classid):
    from flask import session, url_for
    """Calcula y devuelve la URL a la que debe regresar."""
    history = session.get('history', [])
    
    # Si hay al menos dos elementos (la página actual y una anterior)
    if len(history) > 1:
        # El penúltimo elemento es la página anterior
        return history[-2] 
    
    # Si no hay historial suficiente, regresa a la página de inicio o a una predeterminada
    return url_for('list_records', classid=classid, page=1)

def requestLog(dataRequest, userId=None):
    if not userId:
        from flask_login import current_user
        if current_user and current_user.is_authenticated:
            userId = current_user.id
        else:
            userId = None
    from models.develop.requestlog import RequestLog
    from utils.db import db
    import json
    log = RequestLog()
    log.dataRequest = json.dumps(dataRequest, indent=4, ensure_ascii=False)
    log.createdby_id = userId
    db.session.add(log)
    db.session.commit()
    return True

def getClazz(classname):
    # Importar dinámicamente la clase correcta
    module_path = f'models.production.{classname.lower()}'
    model_module = __import__(module_path, fromlist=[classname.lower()])
    modelClass = getattr(model_module, classname.capitalize())
    return modelClass

def saveForm(institution, fields, id=None,data=None):
    from utils.db import db
    from .application import getClazz
    from flask import request
    from datetime import datetime
    from .engine import floatToMoney
    from flask_login import current_user
    
    # Define los diferentes tipos de campos
    checkbox_fields_boolean = {key for key, value in fields.items() if value['type'] == 'Boolean'}
    checkbox_fields = {key for key, value in fields.items() if value['input'] == 'checkbox' and value['type'] != 'Boolean'}
    integer_fields = {key for key, value in fields.items() if value['input'] == 'Integer'}
    money_fields = {key for key, value in fields.items() if value['type'] == 'Money'}
    date_fields = {key for key, value in fields.items() if value['input'] == 'date'}
    blob_fields = {key for key, value in fields.items() if value['type'] == 'blob'}
    parent_fields = {key for key, value in fields.items() if value['type'] == 'selfParent'}
    connected_table_fields = {key for key, value in fields.items() if value['type'] == 'connected_table'}
    hasmany_fields = {key: value for key, value in fields.items() if value.get('hasManyValues') is True}

    # Crea el log del request
    if not data:
        data = request.form
    void = requestLog(data)
    fields_in_request_raw = data.get("fields_in_request")
    if fields_in_request_raw:
        # Convertir la cadena de campos separados por coma a un conjunto (set)
        # Esto nos dice: "Estos son los campos que el usuario vio y pudo haber editado."
        fields_in_request = set(fields_in_request_raw.split(','))
    else:
        # Si no se proporciona la lista, asumimos que es un formulario completo (el comportamiento original)
        fields_in_request = set(fields.keys())
    print(fields_in_request)

    # Itera sobre los campos del formulario que coinciden con los nombres de las columnas
    #print(request.form)
    for key in data:
        valueForm = data.get(key)
        #if valueForm:
        if key in fields and hasattr(institution, key):
            #print(valueForm)
            if key in checkbox_fields_boolean:
                if valueForm == 'on':
                    setattr(institution, key, True)
                else:
                    setattr(institution, key, False)
            elif key in blob_fields:
                fieldname = f"{key}_id"
                if valueForm == '':
                    setattr(institution, fieldname, None)
                else:
                    setattr(institution, fieldname, int(valueForm))
            elif key in parent_fields:
                fieldname = f"{key}_id"
                if valueForm == '':
                    setattr(institution, fieldname, None)
                else:
                    setattr(institution, fieldname, int(valueForm))
            elif key in connected_table_fields and key not in hasmany_fields:
                fieldname = f"{key}_id"
                if valueForm == '':
                    setattr(institution, fieldname, None)
                else:
                    setattr(institution, fieldname, int(valueForm))
            elif key in integer_fields:
                if valueForm == '':
                    setattr(institution, key, None)
                else:
                    setattr(institution, key, int(valueForm))
            elif key in money_fields and valueForm != '':
                if valueForm == '':
                    setattr(institution, key, None)
                else:
                    val = float(valueForm)
                    val = floatToMoney(val)
                    setattr(institution, key, val.getCents())
            elif key in date_fields:
                if valueForm == '':
                    setattr(institution, key, None)
                else:
                    setattr(institution, key, datetime.strptime(valueForm, '%Y-%m-%d').date())
            elif key in checkbox_fields:
                checks = data.getlist(key)
                setattr(institution, key, str(checks) if checks else None)
            elif key not in hasmany_fields:
                value = data.get(key)
                setattr(institution, key, None if valueForm == '' else valueForm)
                #print(f"Seteando {key} = {getattr(institution, key)}")

    # Manejo de relaciones hasMany
    #print(f"HasMany: {hasmany_fields}")
    for key, value in hasmany_fields.items():
        # data vendrá con múltiples IDs seleccionados
        #print(f"Procesando hasMany para {key} con valor: {data.get(key)}")
        raw_value = data.get(key)
        if key in data:
            if not raw_value:
                ids = [] # Lista vacía si no hay valores
            else:
                # El valor debe ser una cadena de IDs separados por coma (ej: "1,5,9")
                ids = [int(x) for x in raw_value.split(",") if x.strip()]
            class_name = getClazz(int(value["connected_table"])).getName()
            model_class = newQuery(class_name)
            related_objects = model_class.getRecords(ids)
            # limpiar y volver a asignar
            getattr(institution, key).clear()
            getattr(institution, key).extend(related_objects)

    # Asegura que los checkboxes no marcados se actualicen como False
    for field in checkbox_fields_boolean:
        # 1. ¿Es un campo booleano? (Si)
        # 2. ¿Estaba este campo en el formulario que se envió? (Verificación con fields_in_request)
        # 3. ¿Se encuentra ausente en los datos POST? (if field not in data)
        if field in fields_in_request and field not in data:
            setattr(institution, field, False)
            
    # Asegura que los checkboxes de otro tipo (e.g., hasMany que usan checkbox) no marcados se actualicen como None
    for field in checkbox_fields:
        if field in fields_in_request and field not in data:
            # Aquí, si es un checkbox de selección múltiple no marcado, se establece a None/vacío
            setattr(institution, field, None) 
    """
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
    """
    # Lógica para manejar nuevos y existentes registros
    try:
        instance_id = int(institution.id)
    except:
        instance_id = None
        
    if not instance_id:
        setattr(institution, "createdby_id", current_user.id)
        db.session.add(institution)
        db.session.commit()
    else:
        setattr(institution, "modifiedby_id", current_user.id)
        db.session.commit()
        
    return institution

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
    QueryInstance = newQuery(classname)
    tableRecord = QueryInstance.getTable()
    return tableRecord

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

def sortTableBy(table, fieldname, reverse=False):
    """Ordena una tabla por un campo específico, manejando valores None.
    :param table: Una lista de objetos o una instancia de la clase `table` que contiene los registros a ordenar.
    :param fieldname: El nombre del atributo (campo) por el cual se desea ordenar los registros.
    :param reverse: Un valor booleano. Si es `True`, la tabla se ordenará en orden descendente.
                    Si es `False` (por defecto), se ordenará en orden ascendente.
    """
    from operator import attrgetter

    def none_safe_key(value):
        # Usa getattr para obtener el valor del campo, manejando None
        field_value = getattr(value, fieldname, None)
        return (field_value is None, field_value if field_value is not None else '')

    fieldsSorted = sorted(table, key=none_safe_key, reverse=reverse)
    return fieldsSorted

def filterTableView(classname):
    from flask import request
    from utils import view_class_container_fields
    fields = view_class_container_fields.get_clazz_fields(classname)
    try:
        query = newQuery(classname)
        for key in request.args:
            if not key.startswith("until-"):
                value = request.args[key]
                if key.startswith("start-"):
                    name = key.split('-')[1]
                    if key in fields:
                        untilName = f"until-{name}"
                        if not request.args[untilName] and value:
                            if value == "isnull":
                                query.addFilter(name, "isnull")
                            elif value == "isnotnull":
                                query.addFilter(name, "isnotnull")
                            else:
                                query.addFilter(name, "==", value)
                        else:
                            query.addFilter(name, ">=", value)
                            valueuntil = request.args[untilName]
                            query.addFilter(name, "<=", valueuntil)

                elif key == "createdBy" and value:
                    query.addFilter("createdby_id", "==", value)
                else:
                    if key in fields and value:
                        name = key
                        if value == "isnull":
                            query.addFilter(name, "isnull")
                        elif value == "isnotnull":
                            query.addFilter(name, "isnotnull")
                        else:
                            is_rel, target_class, is_m2m, is_m2o = query._get_relationship_info(name)
                            if is_rel and is_m2m:
                                query.addFilter(name, "contains_id", value)
                            elif is_rel and is_m2o:
                                query.addFilter(name, "==", value)
                            else:
                                query.addFilter(key, "like", value)
        #table = query.getTable()
        return query
    except Exception as e:
        print(f"Error al filtrar la tabla: {e}")
        return None

def buildTree(categories, name, parent_id=None):
    tree = []
    for cat in [c.getORMRecord() for c in categories if c.get(name) == parent_id]:
        node = {
            "text": cat.name,
            "id": cat.id,
            "children": buildTree(categories, name, cat.id)
        }
        if not node["children"]:  # Si no tiene hijos, eliminar la clave 'children'
            node.pop("children")
        tree.append(node)
    #print(tree)
    return tree

def treeViewJson(classname, name):
    class_table = getTable(classname)
    tree = buildTree(class_table, name)
    return tree

def putVariable(variable,value):
    from flask import session
    session[variable] = value
    return True

def getVariable(variable):
    from flask import session
    return session.get(variable)

def newQuery(classname):
    return Query(classname)

def getEditUrlFromRecord(record):
    """
    Recibe un objeto de registro y devuelve su URL de edición.
    :param record: Instancia del registro.
    :return: URL de edición del registro.
    """
    from utils.packages.application import getClazz
    from flask import url_for
    classid = getClazz(record.__class__.__name__).getId()
    edit_url = url_for('routing.edit_record', record_id=record.id, classid=classid)
    return edit_url

def getViewUrlFromRecord(record):
    """
    Recibe un objeto de registro y devuelve su URL de visualización.
    :param record: Instancia del registro.
    :return: URL de visualización del registro.
    """
    from utils.packages.application import getClazz
    from flask import url_for
    clazz = record.__class__.__name__
    classid = getClazz(clazz).getId()
    view_url = url_for('routing.view_record', record_id=record.id, classid=classid)
    return view_url

class Query:
    def __init__(self, classname):
        # Importar dinámicamente la clase correcta
        from .application import getClazzName
        if isinstance(classname, int):
            class_info = getClazzName(classname)
        elif isinstance(classname, str):
            class_info = getClazzName(classname)
        else:
            raise TypeError("clazz_id debe ser un entero (ID) o una cadena (nombre).")
        
        module_path = f'models.production.{class_info.lower()}'
        model_module = __import__(module_path, fromlist=[class_info.capitalize()])
        modelClass = getattr(model_module, class_info.capitalize())
        self.model_class = modelClass
        self.query = modelClass.query
    
    def set(self):
        return self.model_class
    
    def addFilterDeprecated(self, fieldname, operator, value=None):
        from sqlalchemy import or_,and_ 
        # Definir un diccionario de operadores
        operators = {
            "==": lambda f, v: f == v,
            "!=": lambda f, v: f != v,
            "<": lambda f, v: f < v,
            ">": lambda f, v: f > v,
            "<=": lambda f, v: f <= v,
            ">=": lambda f, v: f >= v,
            "like": lambda f, v: f.ilike(f"%{v}%"),
            "or": lambda f, v: or_(*[f == item for item in v]),
            "and": lambda f, v: and_(*[f == item for item in v]),
            "isnull": lambda f, v: or_(f.is_(None), f == ''),     # IS NULL
            "isnotnull": lambda f, v: and_(f.isnot(None), f != ''), # IS NOT NULL
        }

        # Obtener la función del operador adecuado
        op_func = operators.get(operator)

        if op_func is None:
            raise ValueError(f"Operador no soportado: {operator}")

        # Filtrar por el campo utilizando la función del operador
        self.query = self.query.filter(op_func(getattr(self.model_class, fieldname), value))
        return self

    def _get_relationship_info(self, fieldname):
        from sqlalchemy import inspect
        from sqlalchemy.orm import RelationshipProperty, MANYTOONE

        mapper = inspect(self.model_class)
        
        if fieldname in mapper.relationships:
            prop = mapper.relationships[fieldname]
            #print(f"Propiedad: {prop}")
            if isinstance(prop, RelationshipProperty):
                # Obtener el mapeador de la clase de destino
                target_mapper = prop.mapper
                
                # Obtener la clase de destino a partir del mapeador
                target_class = target_mapper.class_
                
                # Debug:
                #print(f"Target class (Corregido): {target_class}")
                
                # Tipo de relación (MANYTOONE, MANYTOMANY, etc.)
                relation_type = prop.direction 
                print(f"Tipo de relación: {relation_type}")
                # Es M2M si tiene tabla secundaria
                is_many_to_many = (prop.secondary is not None)
                
                # Es M2O si la dirección es MANYTOONE y NO es M2M (para ser precisos)
                is_many_to_one = (relation_type is MANYTOONE and not is_many_to_many)
                
                return (True, target_class, is_many_to_many, is_many_to_one)
        
        return (False, None, None, None)

    def addFilter(self, fieldname, operator, value=None):
        from sqlalchemy import or_, and_, inspect
        import ast 

        # ----------------------------------------------------
        # PASO 1: DEFINICIÓN DE OPERADORES Y VALIDACIÓN INICIAL
        # ----------------------------------------------------
        # Define el diccionario de operadores UNA VEZ.
        operators = {
            "==": lambda f, v: f == v,
            "!=": lambda f, v: f != v,
            "<": lambda f, v: f < v,
            ">": lambda f, v: f > v,
            "<=": lambda f, v: f <= v,
            ">=": lambda f, v: f >= v,
            "like": lambda f, v: f.ilike(f"%{v}%"),
            "in": lambda f, v: f.in_(v), 
            "or": lambda f, v: or_(*[f == item for item in v]),
            "and": lambda f, v: and_(*[f == item for item in v]),
            "isnull": lambda f, v: or_(f.is_(None), f == ''),    
            "isnotnull": lambda f, v: and_(f.isnot(None), f != ''), 
            # Si quieres un operador específico para M2M ID, re-nómbralo a 'contains_id' 
            "contains_id": lambda f, v: f == v, 
        }
        
        # Intenta obtener la función del operador. Si no existe, genera un error, 
        # a menos que sea un operador que se maneja completamente en el bloque de relaciones.
        op_func = operators.get(operator)
        
        # ----------------------------------------------------
        # PASO 2: OBTENER INFO Y MANEJO DE RELACIONES
        # ----------------------------------------------------
        is_rel, target_class, is_m2m, is_m2o = self._get_relationship_info(fieldname)
        # DEBUG
        #print(f"Es relación: {is_rel}")
        if is_rel:
            relation_attribute = getattr(self.model_class, fieldname)
            mapper = inspect(self.model_class)
            filter_condition = None # Inicializa la condición
            
            if is_m2m:
                
                if operator == 'isnotnull':
                    # Objetos CON al menos un valor (WHERE EXISTS)
                    filter_condition = relation_attribute.any() 
                
                elif operator == 'isnull':
                    # Objetos SIN ningún valor (WHERE NOT EXISTS)
                    filter_condition = ~relation_attribute.any()
                
                elif operator == 'in' and isinstance(value, str):
                    try:
                        # Intenta parsear una lista de Python (e.g., '[233, 234]')
                        parsed_value = ast.literal_eval(value)
                        if isinstance(parsed_value, int):
                            parsed_value = [parsed_value]
                        elif not isinstance(parsed_value, list):
                            raise ValueError("M2M 'in' value must be a list or integer string.")
                        value = [int(v) for v in parsed_value] # Convertir a enteros
                    except (ValueError, TypeError, SyntaxError):
                        # Si falla el parseo, asumimos que es una cadena simple que contiene un ID
                        value = [int(v.strip()) for v in value.split(',') if v.strip()]
                
                if operator == 'contains_id' or operator == '==':
                    # Para 'contains_id'/'==', el valor debe ser un entero
                    if isinstance(value, str):
                        try:
                            value = int(value.strip('[]')) # Limpiar posibles corchetes y convertir a int
                        except ValueError:
                            raise ValueError("M2M 'contains_id' value must be a single integer.")

                    filter_condition = relation_attribute.any(
                        getattr(target_class, 'id') == value
                    )
                    
                elif operator == 'in':
                    # 'value' es una lista de enteros
                    filter_condition = relation_attribute.any(
                        getattr(target_class, 'id').in_(value)
                    )
                
            elif is_m2o:
                prop = mapper.relationships[fieldname]
                try:
                    # Obtenemos el objeto Column de SQLAlchemy desde el set
                    local_column_obj = next(iter(prop.local_columns))
                    #print(f"Local column: {local_column_obj}")
                    local_col_name = local_column_obj.name
                    #print(f"Local column name: {local_col_name}")
                    # Accedemos a la columna usando su nombre en la tabla
                    #local_col = prop.local_table.c[local_col_name]
                    local_col = getattr(self.model_class, local_col_name)
                    #print(f"Local column object: {local_col}")
                except StopIteration:
                    # Esto ocurre si prop.local_columns está vacío
                    raise Exception(f"No se pudo determinar la Clave Foránea local para la relación M2O: '{fieldname}'.")
    
                # 1. INTENTO DE FILTRO M2O DE EXISTENCIA (has_any / has_none)
                if operator == 'isnotnull':
                    # Objetos CON cualquier valor (FK IS NOT NULL)
                    filter_condition = local_col.isnot(None)
                    self.query = self.query.filter(filter_condition)
                    return self

                elif operator == 'isnull':
                    # Objetos SIN ningún valor (FK IS NULL)
                    filter_condition = local_col.is_(None)
                    self.query = self.query.filter(filter_condition)
                    return self

                # 2. INTENTO DE FILTRO M2O SIMPLE (POR ID DIRECTO)
                if operator == '==' or operator == '!=':
                    if op_func is not None:
                        filter_condition = op_func(local_col, value)
                        self.query = self.query.filter(filter_condition)
                        return self
            
                    
                if op_func is None:
                    raise ValueError(f"Operador '{operator}' no soportado para M2O: '{fieldname}'.")

                if isinstance(value, tuple) and len(value) == 2:
                    related_field, related_value = value
                    
                    related_column = getattr(target_class, related_field)
                    
                    inner_condition = op_func(related_column, related_value)
                    
                    filter_condition = relation_attribute.has(inner_condition)
                    # Aplica el filtro has() y retorna
                    self.query = self.query.filter(filter_condition)
                    return self

                #print("estoy aqui 2")
                # Si el valor no es una tupla y no se capturó como filtro simple ID
                raise ValueError(f"El filtro M2O requiere un valor en formato (campo_relacionado, valor) o un ID simple con '==' / '!='.")    

            # Verifica si la lógica anterior definió un filtro
            if filter_condition is not None:
                self.query = self.query.filter(filter_condition)
                return self
            
            # Si es una relación, pero no se cumplen las condiciones M2M o M2O
            raise ValueError(f"Operador '{operator}' no soportado o uso incorrecto para la relación '{fieldname}'.")
            
        # ----------------------------------------------------
        # PASO 3: MANEJO DE COLUMNAS SIMPLES
        # ----------------------------------------------------
        else:
            # En el caso de columnas simples, el operador DEBE estar en el diccionario
            if op_func is None:
                raise ValueError(f"Operador no soportado: {operator}")

            field = getattr(self.model_class, fieldname)
            self.query = self.query.filter(op_func(field, value))
            print("O aqui termina")
            return self
       
    def getSum(self, fieldname):
        from sqlalchemy import func
        # Obtener la suma del campo especificado
        result = self.query.with_entities(func.sum(getattr(self.model_class, fieldname))).scalar()
        return result or 0

    def getSumBy(self, fieldname, groupby):
        from sqlalchemy import func
        # Obtener la suma del campo especificado agrupado por otro campo
        result = self.query.with_entities(func.sum(getattr(self.model_class, fieldname)), getattr(self.model_class, groupby)).group_by(getattr(self.model_class, groupby)).all()
        return result or 0
    
    def getCountBy(self, fieldname, groupby):
        from sqlalchemy import func
        result = self.query.with_entities(
            getattr(self.model_class, groupby),
            func.count(getattr(self.model_class, fieldname))
        ).group_by(getattr(self.model_class, groupby)).all()
        return result or []

    def filterByToday(self):
        from datetime import datetime, timezone
        from sqlalchemy.sql import func

        today = datetime.now(timezone.utc).date() 
        model = self.model_class

        # Aplicar el filtro sin ejecutar la consulta
        self.query = self.query.filter(func.date(model.created_at) == today)

        return self

    def getTableQuery(self):
        return self.query
    
    def getTable(self):
        """Devuelve una instancia de table con todos los registros."""
        raw_records = self.query.all()
        record_instances = [Record(record_object=record) for record in raw_records]
        return table(self.model_class, record_instances)
    
    def getRecords(self, related_ids):
        # Devuelve una instancia de table con los registros filtrados
        records = self.model_class.query.filter(self.model_class.id.in_(related_ids)).all()
        return records
    
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
    
    def toSession(self):
        ids_seleccionados = [obj.id for obj in self.query.all()]
        from flask import session
        session["table"] = ids_seleccionados
        return True
    def getRecordsFromSession(self):
        from flask import session
        ids_seleccionados = session.get("table")
        if ids_seleccionados:
            #print(type(ids_seleccionados))
            #print(ids_seleccionados)
            return self.model_class.query.filter(self.model_class.id.in_(ids_seleccionados)).all()

    def getTwoWayCount(self, fieldname, group_by_field):
        from sqlalchemy import func
        """
        Calcula la distribución (conteo) de un campo (fieldname) 
        desagregada por otro campo (group_by_field).
        
        Ej: Contar las opciones de 'campo1' separadas por 'gender'.
        """
        
        # 1. Obtener los objetos Column de SQLAlchemy
        group_col = getattr(self.model_class, group_by_field)
        field_col = getattr(self.model_class, fieldname)

        # 2. Ejecutar la consulta con GROUP BY de doble columna
        # IMPORTANTE: Usamos self.query, que ya incluye los filtros aplicados previamente.
        result = self.query.with_entities(
            group_col.label(group_by_field),
            field_col.label(fieldname),
            # Usar func.count() (o func.count('*')) cuenta el número de filas
            func.count().label('count') 
        ).group_by(group_col, field_col).all()
        
        return result
    
    def getMultiFieldStats(self, fields_to_count, group_by_field):
        """
        Función de alto nivel para obtener estadísticas de múltiples campos
        y devolverlas en un diccionario estructurado.
        """
        all_stats = {}
        for fieldname in fields_to_count:
            # Llama a la función de conteo de doble vía por cada campo
            raw_results = self.getTwoWayCount(fieldname, group_by_field)
            
            # Formatea los resultados en un diccionario más útil
            field_stats = {}
            for group_value, field_value, count in raw_results:
                # La clave principal es el valor del campo ('Sí', 'No', 'NS')
                if field_value not in field_stats:
                    field_stats[field_value] = {}
                
                # La clave secundaria es el valor de la agrupación ('Hombre', 'Mujer')
                field_stats[field_value][group_value] = count
            
            all_stats[fieldname] = field_stats
            
        return all_stats
    
class table:
    def __init__(self, model_class, records=None):
        self.model_class = model_class
        self._records = records  # Puede ser None o una lista de registros
    
    def __iter__(self):
        """Hace que la instancia sea iterable."""
        return iter(self._records)

    def __len__(self):
        """Devuelve el número de registros."""
        return len(self._records)
    
    def size(self):
        return len(self._records)
    
    def set(self):
        return self.model_class
           
    def getFilteredTable(self, fieldname, operator, value):
        operators = {
            "==": lambda f, v: f == v,
            "!=": lambda f, v: f != v,
            "<": lambda f, v: f < v,
            ">": lambda f, v: f > v,
            "<=": lambda f, v: f <= v,
            ">=": lambda f, v: f >= v,
            "like": lambda f, v: v.lower() in getattr(f, fieldname).lower() if getattr(f, fieldname) else False,
            "in": lambda f, v: getattr(f, fieldname) in v if getattr(f, fieldname) is not None else False
        }
        op_func = operators.get(operator)
        if op_func is None:
            raise ValueError(f"Operador no soportado: {operator}")
        
        # El cambio clave: ahora el filtro se aplica al objeto encapsulado .record
        if operator in ["like", "in"]:
            # Operadores con lógica Python pura
            filtered_records = [r for r in self._records if op_func(r.record, value)]
        else:
            # Operadores estándar
            filtered_records = [r for r in self._records if op_func(getattr(r.record, fieldname), value)]
        
        return table(self.model_class, filtered_records)

    def groupBy(self, fieldname):
        """
        Agrupa los registros por el valor del campo especificado.
        
        :param fieldname: Nombre del campo por el cual agrupar.
        :return: Diccionario donde las claves son los valores únicos del campo y los valores son listas de registros.
        """
        import collections
        grouped_data = collections.defaultdict(list)
        for record_instance in self._records:
            key = getattr(record_instance.record, fieldname)
            grouped_data[key].append(record_instance)
        return grouped_data
    
    def getFirstRecord(self):
        """
        Devuelve el primer registro de la lista, si existe.
        Devuelve None si la lista de registros está vacía.
        """
        if self._records:
            return self._records[0]
        return None
    
    def getRecord(self, index=0):
        """
        Devuelve el registro en la posición 'index' de la lista, si existe.
        Devuelve None si la lista de registros está vacía.
        """
        if self._records:
            if 0 <= index < len(self._records):
                return self._records[index]
        return None
    
    def getLastRecord(self):
        """
        Devuelve el último registro de la lista, si existe.
        Devuelve None si la lista de registros está vacía.
        """
        if self._records:
            return self._records[-1]
        return None
    
class Record:
    def __init__(self, classname=None, record_id=None, record_object=None):
        if record_object:
            self.record = record_object
        elif classname and record_id:
            module_path = f'models.production.{classname.lower()}'
            model_module = __import__(module_path, fromlist=[classname.capitalize()])
            modelClass = getattr(model_module, classname.capitalize())
            self.record = modelClass.query.get_or_404(record_id)
        else:
            raise ValueError("You must provide either a record object or a classname and record_id.")
        
    def getORMRecord(self):
        return self.record
    
    def store(self, label, value):
        if hasattr(self.record, label):
            setattr(self.record, label, value)
            from utils.db import db
            db.session.commit()  # Asegúrate de usar db.session.commit() para confirmar los cambios
            return True
        return False

    def getConnectedTable(self, tableName):
        from utils.packages.application import getClazz
        # Obtener la clase del nombre de la tabla conectada
        clazz = getClazz(tableName)
        # Obtener el nombre plural de la tabla conectada
        plural = clazz.plural
        
        # Obtener los registros conectados
        connected_records = getattr(self.record, plural, None)
        if connected_records is not None:
            return connected_records
        else:
            raise AttributeError(f"No connected table named '{tableName}' found for the record.")

    def get(self, label):
        # Acceder al atributo del registro
        return getattr(self.record, label, None)
    
    def getEditUrl(self):
        from utils.packages.application import getClazz
        from flask import url_for
        classid = getClazz(self.record.__class__.__name__).getId()
        edit_url = url_for('routing.edit_record', record_id=self.record.id, classid=classid)
        return edit_url
    
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
        return Record(record_object=self.record)
    