# -*- coding: utf-8 -*- 
import os
import keyword
from utils.packages import application, session
from config import databaseType

def is_safe_name(name):
    """ Verifica si el nombre es seguro para usar como nombre de variable o clase """
    return name.isidentifier() and not keyword.iskeyword(name)

def validate_field(field):
    """ Valida que el campo contenga datos seguros y apropiados para generar código """
    safe_types = {'Integer':'Integer',
                  'createdby':'createdby',
                  'modifiedby':'modifiedby',
                  'modificationDate':'modificationDate',
                  'creationDate':'creationDate',
                  'String':'String',
                  'Money':'Money',
                  'Text':'Text',
                  'Boolean':'Boolean',
                  'Date':'Date',
                  'Time':'Time',
                  'Datetime':'Datetime',
                  'JSON':'JSON',
                  'connected_table':'connected_table',
                  'selfParent':'selfParent',
                  'blob':'blob',
                  'calculate':'calculate'}
    if not is_safe_name(field['name']) or field['type'] not in safe_types:
        print("Invalid field data")
        print(f"Field name: {field['name']}, Field type: {field['type']}")
        raise ValueError("Invalid field data")

def clear_file_content(file_path):
    """
    Borra el contenido de un archivo.
    
    Args:
    file_path (str): La ruta al archivo cuyo contenido se desea borrar.
    """
    try:
        # Abrir el archivo en modo de escritura, lo que truncará el archivo a 0 bytes
        with open(file_path, 'w'):
            pass
        print(f"El contenido del archivo {file_path} ha sido borrado.")
    except Exception as e:
        print(f"Se produjo un error al intentar borrar el contenido del archivo: {e}")

def ensure_import_exists(file_path, import_statement):
    try:
        # Leer el contenido actual del archivo
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Verificar si el import ya existe
        import_exists = any(import_statement in line for line in lines)

        # Si el import no existe, agregarlo al final del archivo
        if not import_exists:
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write('\n' + import_statement )
            print(f"'{import_statement}' fue agregado al archivo.")
        else:
            print(f"'{import_statement}' ya existe en el archivo.")

    except Exception as e:
        print(f"Error al manejar el archivo: {e}")

def generate_model_class(fields, class_name, file_name, directory, plural, relevants):
    clazz = application.getClazzDevelop(class_name)

    """ Genera una clase de modelo SQLAlchemy basada en los campos proporcionados """
    # Valida el nombre de la clase
    if not is_safe_name(class_name):
        print("Invalid class name")
        raise ValueError("Invalid class name")
    file_path = os.path.join(directory, file_name)
    
    # Asegura que el directorio exista
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Inicializa variables para la definición de la clase
    class_definition = f"class {class_name.capitalize()}(db.Model):\n    __tablename__ = '{class_name.lower()}'\n    id = db.Column(db.Integer, primary_key=True)\n"
    

    # Revisa si se debe generar el método __repr__
    if clazz and clazz.clazz_representation:
        representation = "    def __repr__(self) -> str:\n"
        representation += """        return self.full_repr """

        # Itera sobre cada línea de la representación
        rep = clazz.clazz_representation
        clazzRepresentation = ""

        for line in rep.split(","):
            parts = line.split("|")
            if len(parts) == 3:
                # Construye la cadena de representación
                first = parts[0]
                second = parts[1]
                third = parts[2]
                
                # Asegúrate de que si algún campo es None, se reemplaza por una cadena vacía
                clazzRepresentation += f"{first}{{self.{second} if self.{second} is not None else ''}}{third}"
            else:
                print("Cada línea de representación debe tener exactamente 3 partes separadas por '|'.")
                raise ValueError("Cada línea de representación debe tener exactamente 3 partes separadas por '|'.")
        
        fullRepr = "\n    @hybrid_property\n"
        fullRepr += "    def full_repr(self):\n"
        fullRepr += f"""        result = f'''{clazzRepresentation}'''\n"""
        fullRepr += """        return result.strip()\n"""

        sql_logic = 'literal_column("''")' # Inicializa la lógica con una cadena vacía

        for line in rep.split(","):
            parts = line.split("|")
            if len(parts) == 3:
                first, field_name, third = parts
                sql_logic += f""" + literal_column("'{first}'") """
                sql_logic += f""" + func.coalesce(cls.{field_name}, literal_column("''")) """
                sql_logic += f""" + literal_column("'{third}'")"""

        # Inicializa slqExp como una cadena vacía
        sqlExp = "\n" 

        # Acumula las líneas de definición del método
        sqlExp += f"""    @full_repr.expression\n"""
        sqlExp += f"""    def full_repr(cls):\n"""
        sqlExp += f"""        return (\n"""
        # Insertamos la lógica SQL generada, INDENTADA correctamente
        sqlExp += f"""            {sql_logic}\n"""
        sqlExp += f"""        )\n\n"""
    else:
        clazzRepresentation = False
     

    # Variables para manejo de ordenamiento por defecto
    if clazz and clazz.sort_field_results:
        sortField = clazz.sort_field_results.split("|")
        sort_column = sortField[0]
        print(fields)
        print(sort_column)
        sort_field_column = fields.get(sort_column)
        if sort_field_column and sort_field_column['type'] == 'connected_table':
            sort_column = f"{sort_column}_id"
        sort_direction = sortField[1]

    property_field = f"\n"
    #print(fields)
    for field_name, field in fields.items():
        
        validate_field(field)
        
        system_type_field = ['modificationDate', 'creationDate', 'modifiedby', 'createdby']

        # Maneja los diferentes tipos de campos
        if field['hasManyValues']:
            # Maneja relaciones muchos a muchos
            record = application.getClazzDevelop(field['connected_table'])
            classname = record.name
            fieldname = f"{field['name']}"
            class_definition += f"    {class_name.lower()}_{classname.lower()} = db.Table( '{class_name.lower()}_{classname.lower()}', db.Column('{class_name.lower()}_id', db.Integer, db.ForeignKey('{class_name.lower()}.id'), primary_key=True), db.Column('{classname.lower()}_id', db.Integer, db.ForeignKey('{classname.lower()}.id'), primary_key=True) )\n"
            class_definition += f"    {fieldname} = db.relationship('{classname.capitalize()}', secondary={class_name.lower()}_{classname.lower()}, lazy='subquery',backref=db.backref('{plural.lower()}', lazy='subquery') )\n"
        
        elif field['type'] == 'selfParent':
            # Maneja relaciones jerárquicas (auto-referenciadas)
            record = application.getClazzDevelop(field['connected_table'])
            classname = record.name
            fieldname = f"{field['name']}"
            class_definition += f"    {fieldname}_id = db.Column(db.Integer, db.ForeignKey('{class_name.lower()}.id', ondelete='CASCADE'), nullable=True)\n"
            class_definition += f"    {fieldname} = db.relationship('{class_name.capitalize()}', remote_side=[id], backref=db.backref('{fieldname}_childs'))\n"
        

        elif field['type'] == 'blob':
            # Maneja campos de tipo blob (Referencia a tabla Blob)
            fieldname = f"{field['name']}"
            class_definition += f"    {fieldname}_id = db.Column(db.Integer, db.ForeignKey('blob.id'), nullable=True)\n"
            class_definition += f"    {fieldname} = db.relationship('Blob', foreign_keys=[{fieldname}_id], lazy='joined')\n"

        elif field['type'] == 'connected_table':
                    # Maneja relaciones uno a muchos (Foreign Records)
                    record = application.getClazzDevelop(field['connected_table'])
                    classname = record.name
                    fieldname = f"{field['name']}"
                    class_definition += f"    {fieldname}_id = db.Column(db.Integer, db.ForeignKey('{classname.lower()}.id', ondelete='CASCADE'), nullable=True)\n"
                    
                    # Base de la definición de la relación Foreign Records (tablas conectadas)
                    referenced_class = classname.capitalize()
                    relationship_base = f"db.relationship('{referenced_class}', backref=backref('{plural}', "
                    relationship_end = "cascade='all, delete-orphan', passive_deletes=True))\n"
                    
                    # Si el campo es el definido como sortField, agrega el order_by correspondiente
                    if sortField and sort_direction == "asc":
                        order_expression = f"order_by='{class_name.capitalize()}.{sort_column}'"
                        class_definition += f"    {fieldname} = {relationship_base}{order_expression},{relationship_end}"
                    elif sortField and sort_direction == "desc":
                        order_expression = f"order_by=lambda: desc({class_name.capitalize()}.{sort_column})"
                        class_definition += f"    {fieldname} = {relationship_base}{order_expression},{relationship_end}"
                    else:
                        class_definition += f"    {fieldname} = {relationship_base}{relationship_end}"
                        
        elif field['type'] == 'Money':
            class_definition += f"    {field['name']} = db.Column(BigInteger(), nullable=True)\n"

        elif field['type'] not in system_type_field:
            # Maneja campos simples
            type_map = {
                'String': 'String',
                'Integer': 'Integer',
                'Time': 'Time',
                'Date': 'Date',
                'DateTime': 'DateTime',
                'Text': 'Text',
                'Boolean': 'Boolean'
            }
            python_type = type_map.get(field['type'], 'String')

            # Establece una longitud máxima por defecto para campos String si no se proporciona
            max_length = f"{field['maxlength'] if field['maxlength'] else 255}" if field['type'] == 'String' else ""

            class_definition += f"    {field['name']} = db.Column(db.{python_type}({max_length}))\n"
        
        if field["helper"] == "script":
            # Maneja campos de tipo calculado
            fieldname = f"{field['name']}"
            calculate_file = field['calculate_file']
            calculate_function = field['calculate_function']
            property_field += f"    def helper_{fieldname}(self):\n"
            property_field += f"        from scripts.{calculate_file} import {calculate_function}\n"
            property_field += f"        result = {calculate_function}(self)\n"
            property_field += f"        self.{fieldname} = result\n"
            property_field += f"        try:\n"
            property_field += f"            db.session.add(self) \n"
            property_field += f"            db.session.commit() \n"
            property_field += f"        except Exception as e:\n"
            property_field += f"            db.session.rollback()\n"
            property_field += f"            raise \n"
            property_field += f"        return self.{fieldname}\n"
            
    # Agrega campos de auditoría
    class_definition += f"    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))\n"
    class_definition += f"    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))\n"
    class_definition += f"    createdby = db.relationship('User', backref='created_{plural}', foreign_keys=[createdby_id])\n"
    class_definition += f"    modifiedby = db.relationship('User', backref='modified_{plural}', foreign_keys=[modifiedby_id])\n"
    class_definition += f"    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))\n"
    class_definition += f"    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))\n"
    
    # Agrega configuración específica para MySQL
    collation = "\n    __table_args__ = {\n"
    collation += """        "mysql_charset": "utf8mb4",\n"""
    collation += """        "mysql_collate": "utf8mb4_unicode_ci",\n"""
    collation += """    }\n"""

    # Define los campos de la clase
    fieldsDefinition = "\n\n"
    fieldsDefinition += f"def get_fields():\n"
    fieldsDefinition += f"    fields = {fields}\n"
    fieldsDefinition += f"    return fields\n"

    # Define las relevancias de la clase
    relevantsDefinition = "\n\n"
    relevantsDefinition += f"def get_relevants():\n"
    relevantsDefinition += f"    relevants = {relevants}\n"
    relevantsDefinition += f"    return relevants\n"

    # Agrega configuración de mapeo si es necesario (ordenamiento por defecto)
    if sortField:
        if sort_direction == "asc":
            sort_definition = f"\n    __default_ordering__ = [{sort_column}]\n"
        else:
            sort_definition = f"\n    __default_ordering__ = [desc('{sort_column}')]\n"

    # Escribe la definición de la clase en el archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("from utils.db import db\n")
        f.write("from sqlalchemy.orm import backref\n")
        f.write("from sqlalchemy import BigInteger\n")
        f.write("from datetime import datetime, timezone \n")
        f.write("from sqlalchemy import desc, func, String, case, literal_column  \n")
        f.write("from sqlalchemy.ext.hybrid import hybrid_property \n")
        f.write("from sqlalchemy.sql.expression import null \n\n")
        f.write(class_definition)
        f.write(property_field)
        
        if(clazzRepresentation):
            f.write(fullRepr)
            f.write(sqlExp)
            f.write(representation)
        f.write(sort_definition)
        if databaseType == "mysql":
            f.write(collation)
        
        f.write(fieldsDefinition)
        f.write(relevantsDefinition)
    message = f"Class {class_name} has been written to {file_path}"

    return message
