#!/bin/bash

# Instalar Flask
pip install Flask

# Instalar Flask-WTF (opcional, si se usan formularios con validación)
pip install Flask-WTF

# Instalar Flask-Bootstrap (opcional, para integrar Bootstrap en Flask)
pip install Flask-Bootstrap

# Instalar WTForms (para manejar formularios en Flask)
pip install WTForms

# Instalar qrcode (para generar códigos QR)
pip install qrcode[pil]

# Instalar Pillow (para trabajar con imágenes, necesario para qrcode)
pip install Pillow

# Instalar Flask-SQLAlchemy (opcional, si se utiliza SQLAlchemy para bases de datos)
pip install Flask-SQLAlchemy

# Instalar pdfkit (si se generan PDFs)
pip install pdfkit

# Mostrar un mensaje de finalización
echo "¡Todas las dependencias han sido instaladas correctamente!"
