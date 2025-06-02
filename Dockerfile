FROM python:3.13-slim

WORKDIR /app

# Copiar requirements y crear carpeta src
COPY requirements.txt ./
RUN mkdir src

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Establecer directorio de trabajo en src
WORKDIR /app/src

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
