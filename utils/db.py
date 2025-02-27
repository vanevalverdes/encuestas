from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

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