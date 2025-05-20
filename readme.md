## Instrucciones para clonar y ejecutar los servidores del backend de gestión de documentos y maestro de materiales

## 1. Clonar el repo del backend:

-Instalar git, python y luego clonar el repo usando `git clone` y la dirección del repo

[felix-jvm/app-documentos-backend.git](felix-jvm/app-documentos-backend.git)

[felix-jvm/maestromateriales-backend.git](felix-jvm/maestromateriales-backend.git)


## 2. Instalación de dependencias:

-Luego de clonar el repo, navegar hasta la ruta donde se descargó, localizar el archivo requirements.txt e instalar dependencias con `pip install -r requirements.txt`

## 3. Configuración de la base de datos:

-Luego de instalar las dependencias, especificar los detalles de la DB en el diccionario `DATABASES` dentro del archivo `settings.py`

## 4. Correr migraciones:

-Luego de configurar la DB, ubicarse donde esta el archivo `manage.py` y ejecutar `python manage.py migrate`

## 5.Ejecutar servidor:

-Luego de ejecutar las migraciones, ejecutar el servidor con `python manage.py runserver` 🚀