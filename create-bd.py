import sqlite3
from pathlib import Path

# Definir la ruta al archivo de la base de datos
base_dir = Path(__file__).parent.resolve()
db_path = base_dir / 'database' / 'data.db'

# Asegurarse de que el directorio de la base de datos exista
db_path.parent.mkdir(parents=True, exist_ok=True)

# Crear la base de datos y establecer la conexión
conn = sqlite3.connect(db_path)

# Crear un cursor
cursor = conn.cursor()

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()

print(f"Base de datos creada en {db_path}")
