# Imagen base con Python
FROM public.ecr.aws/amazonlinux/amazonlinux:2023

# Instalar Python y pip
RUN dnf install -y python3.11 python3.11-pip && \
    alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    alternatives --install /usr/bin/pip pip /usr/bin/pip3.11 1

# Crear directorio de la app
WORKDIR /app

# Copiar requerimientos primero (para aprovechar caché de Docker)
COPY requirements.txt .

# Instalar dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto (ejemplo FastAPI con uvicorn en 5000)
EXPOSE 5000

