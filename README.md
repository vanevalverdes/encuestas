# BaaS - Flask

## Información General

El actual proyecto se basa en Flask como framework para desarrollar un Backend as a Service, integrando interfaces gráficas para la administración de los modelos, las vistas, formularios,  enrutamientos, RESTAPI y autenticación de usuarios.

La versión actual está configurada para trabajar con MySQL, aunque es compatible con SQLite y otras Bases de datos SQL, ajustando algunos parámetros.

Esta versión incluye los archivos .cpanel.yml y passenger_wsgi.py, necesarios para el deploy en CPanel a través Application Manager y control de versiones de GIT.

## Estructura

La incialización del proyecto se realiza a través del index.py:

> python index.py

Su estructura básica es:
<pre> ```
/proyecto
    LICENSE
    README.md
    .env
    .cpanel.yml
    app.py
    index.py
    config.py
    requirements.txt
    passenger_wsgi.py
    /models
        /develop
        /application
            clazzlist.py
    /routes
        /develop
        routing.py
    /static
    /uploads
    /templates
        /backend
        /frontend
    /utils
        /packages
``` </pre>

### Archivo .env

Para las variables de entorno, se utiliza el archivo .env con las siguientes definiciones:
<pre> ```
DATABASE_TYPE=mysql
APPLICATION_NAME=
ADMIN_MAIL=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_HOST=
MYSQL_PORT=
MYSQL_DB=
MAIL_PORT=
MAIL_USE_TLS=
MAIL_USE_SSL=
MAIL_SERVER=
MAIL_USERNAME=
MAIL_PASSWORD=
SECRET_KEY=
UPLOAD_FOLDER=uploads
``` </pre>

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Consultá el archivo [LICENSE](./LICENSE) para más información.
