FROM python:3.8.3-alpine

#Establecer directorio de trabajo
WORKDIR /usr/src/app

#Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#instalamos las dependencias
RUN pip install --upgrade pip
COPY requerimientos.txt .
RUN apk update && apk add postgresql-dev gcc python3-dev jpeg-dev zlib-dev musl-dev
RUN pip install -r requerimientos.txt

#Copiamos el proyecto
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]