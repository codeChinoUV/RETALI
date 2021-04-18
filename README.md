# RETALI
El Repositorio de Tareas en Linea (RETALI) es una plataforma Web que 
permite a sus usuarios (alumnos y maestros) crear y unirse a clase, crear,
entregar y revisar actividades, participar en foros, crear y ver avisos.

### Despliegue en producción
1. Modificar las variables de entorno correspondientes a la base de datos en el archivo .env.prod.db
```
    POSTGRES_USER=PUT_YOUR_USER
    POSTGRES_PASSWORD=PUT_YOUR_PASSWORD
    POSTGRES_DB=PUT_YOUR_DB
```
2. Modificar las siguientes variables de entorno del archivo .env.prod
```
    SECRET_KEY=PUT_YOUR_SECRET_KEY
    DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1] PUT_IP_SERVER
    SQL_DATABASE=PUT_YOUR_DB
    SQL_USER=PUT_YOUR_USER
    SQL_PASSWORD=PUT_YOUR_PASSWORD
    EMAIL_HOST_USER=PUT_YOUR_EMAIL
    EMAIL_HOST_PASSWORD=PUT_YOUR_EMAIL_PASSWORD
```
SQL_DATABASE, SQL_PASSWORD y SQL_USER, deben de ser los mismos valores colocados en las variables de entorno de la base
de datos .env.prod.db
3. Contruye los contenedores con el archivo de docker-compose de producción
```
    docker-compose -f docker-compose.prod.yml build
```
4. Levanta los contenedores con el comando
```
    docker-compose -f docker-compose.prod.yml up -d
```
5. Crea las tablas de la base de datos migrando los modelos
```
    docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
```
6. Recolecta los archivos staticos 
```
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
```
7. Si no se visualizan los archivos estaticos baja los contenedores y vuelve a levantarlos
```
    docker-compose -f docker-compose.prod.yml down -v
    docker-compose -f docker-compose.prod.yml up -d
```
