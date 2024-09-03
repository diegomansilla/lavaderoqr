#Usa imagen de Python
FROM python:3.12-slim

#Directorio de trabajo
WORKDIR /app

# Copia los archivos de requisitos y la aplicación al contenedor
COPY requirements.txt requirements.txt
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Instala Apache y mod_wsgi
RUN apt-get update && \
    apt-get install -y apache2 libapache2-mod-wsgi-py3 && \
    apt-get clean

# Copia el archivo de configuración de Apache
COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

# Expone el puerto 80
EXPOSE 80

# Inicia Apache en primer plano
CMD ["apachectl", "-D", "FOREGROUND"]