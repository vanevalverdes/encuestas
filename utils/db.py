from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Define las convenciones de nombres
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Crea el objeto MetaData con las convenciones
metadata = MetaData(naming_convention=convention)

# Pasa el metadata a SQLAlchemy
db = SQLAlchemy(metadata=metadata)

# Habilita claves foráneas en SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    from sqlite3 import Connection as SQLite3Connection
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()