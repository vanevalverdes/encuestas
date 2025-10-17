import os
import keyword
from utils.methods import application, session
from config import databaseType

def is_safe_name(name):
    """ Verifica si el nombre es seguro para usar como nombre de variable o clase """
    return name.isidentifier() and not keyword.iskeyword(name)

def validate_field(field):
    """ Valida que el campo contenga datos seguros y apropiados para generar código """
    safe_types = {'Integer': 'Integer','createdby': 'createdby','modifiedby': 'modifiedby','modificationDate': 'modificationDate','creationDate': 'creationDate', 'String': 'String', 'Money':'Money', 'Text':'Text', 'Boolean': 'Boolean', 'Date': 'Date', 'Time': 'Time', 'Datetime': 'Datetime', 'JSON': 'JSON', 'connected_table':'connected_table'}
    if not is_safe_name(field['name']) or field['type'] not in safe_types:
        print("Invalid field data")
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
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Verificar si el import ya existe
        import_exists = any(import_statement in line for line in lines)

        # Si el import no existe, agregarlo al final del archivo
        if not import_exists:
            with open(file_path, 'a') as file:
                file.write('\n' + import_statement )
            print(f"'{import_statement}' fue agregado al archivo.")
        else:
            print(f"'{import_statement}' ya existe en el archivo.")

    except Exception as e:
        print(f"Error al manejar el archivo: {e}")

def generate_model_class(fields, class_name, file_name, directory, plural):

    if not is_safe_name(class_name):
        print("Invalid class name")
        raise ValueError("Invalid class name")
    file_path = os.path.join(directory, file_name)
    
    if not os.path.exists(directory):
        os.makedirs(directory)

    class_definition = f"class {class_name.capitalize()}(db.Model):\n    __tablename__ = '{class_name.lower()}'\n    id = db.Column(db.Integer, primary_key=True)\n"
    recordRepresentation = application.getClazzDetails(class_name)
    if recordRepresentation.getRepresentation():
        clazzRepresentation = "    def __repr__(self) -> str:\n"
        clazzRepresentation += """        return f" """

        # Itera sobre cada línea de la representación
        rep = recordRepresentation.getRepresentation()
        
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
        
        clazzRepresentation += """"\n"""
    else:
        clazzRepresentation = False

    #print(fields)
    for field in fields:
        

        validate_field(field)

        if field['type'] == 'connected_table':
            record = application.getClazzDetails(field['connected_table'])
            classname = record.getName()
            fieldname = f"{field['name']}"
            class_definition += f"    {fieldname} = db.Column(db.Integer, db.ForeignKey('{classname.lower()}.id'), nullable=True)\n"
            class_definition += f"    {classname.lower()} = db.relationship('{classname.capitalize()}', backref='{plural}')\n"
        elif field['type'] != 'modificationDate' and field['type'] != 'creationDate' and field['type'] != 'modifiedby' and field['type'] !='createdby':
            python_type = 'String' if field['type'] == 'String' else 'Integer' if field['type'] == 'Integer' else 'Time' if field['type'] == 'Time' else 'Date' if field['type'] == 'Date' else 'DateTime' if field['type'] == 'DateTime' else 'Integer' if field['type'] == 'Money' else 'Text' if field['type'] == 'Text' else 'Boolean'
            max_length = f"{field['maxlength'] if field['maxlength'] else 255}" if field['type'] == 'String' else ""
            class_definition += f"    {field['name']} = db.Column(db.{python_type}({max_length}))\n"

    class_definition += f"    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))\n"
    class_definition += f"    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))\n"
    class_definition += f"    createdby = db.relationship('User', backref='created_{plural}', foreign_keys=[createdby_id])\n"
    class_definition += f"    modifiedby = db.relationship('User', backref='modified_{plural}', foreign_keys=[modifiedby_id])\n"
    class_definition += f"    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))\n"
    class_definition += f"    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))\n"
    
    collation = "\n    __table_args__ = {\n"
    collation += """        "mysql_charset": "utf8mb4",\n"""
    collation += """        "mysql_collate": "utf8mb4_unicode_ci",\n"""
    collation += """    }\n"""
    
    with open(file_path, 'w') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("from utils.db import db\n")
        f.write("from datetime import datetime, timezone \n")
        f.write(class_definition)
        if(clazzRepresentation):
            f.write(clazzRepresentation)
        if databaseType == "mysql":
            f.write(collation)

    message = f"Class {class_name} has been written to {file_path}"

    return message
