import subprocess
import traceback
from datetime import datetime
from flask_login import current_user
from config import flask_executable

#flask_executable = '/root/engine/develop/venv/bin/flask'

def migrateClass():
    username = current_user.email.replace("'", "\\'").replace('"', '\\"')
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    messageUpdate = f"Actualizacion de Base de datos hecha por {username} a las: {date_str}"

    # Ejecutar el comando de migración
    try:
        subprocess.run([flask_executable, 'db', 'migrate', '-m', messageUpdate], check=True)
        subprocess.run([flask_executable, 'db', 'upgrade'], check=True)
        print("Database migration and upgrade completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Subprocess failed:", e)
        print(f"An error occurred while running the database migration: {e}")
        print(traceback.format_exc())
        raise
