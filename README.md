<h1 align="center">📡 Proyecto 1 – Sistema P2P con REST & gRPC</h1>

<p align="center">
  <b>Arquitecturas de Nube y Sistemas Distribuidos – UPB</b> <br/>
  <i>Diseño e implementación de un sistema P2P descentralizado con microservicios</i>
</p>

---

## 🚀 Tecnologías usadas

<p align="center">
  <img src="https://img.shields.io/badge/REST-API-blue?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/gRPC-Protocol-orange?style=for-the-badge&logo=grpc&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS-Academy-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white"/>
  <img src="https://img.shields.io/badge/Microservices-Architecture-9cf?style=for-the-badge&logo=microgenetics&logoColor=black"/>
</p>

---

## 🎯 Objetivos
- Diseñar e implementar un sistema **P2P** con múltiples peers.  
- Usar **REST API** y **gRPC** para la comunicación entre procesos.  
- Soportar **concurrencia** en el servidor.  
- Desplegar el sistema en **Docker** y **AWS Academy**.  

---

## 🏗️ Arquitectura

📌 El sistema está compuesto por:  
- **PServidor** → Microservicios que manejan consultas, localización y ECO upload/download.  
- **PCliente** → Interactúa con otros peers y solicita recursos.  

📂 Microservicios principales:  
- 📑 Listado y consulta de archivos.  
- 🔍 Localización de archivos en la red.  
- ⬆️ ECO Upload (simulación de carga).  
- ⬇️ ECO Download (simulación de descarga).
- ⬆️ grpc Upload y Download(Transferencia real).  

---

## ⚙️ Usar el sistema Implementacion_Nube
# 🌩️ Sistema de Implementación en Nube

## 📋 Información de la Cuenta

*Cuenta AWS:* Maria Lucia Cadavid Martinez  
*Correo:* maria.cadavidm@upb.edu.co

---

## 🚀 Configuración Inicial

### 1. Clonar el Repositorio
bash
git clone https://github.com/luu1003/proyecto1_arquitecturaDeNube.git
cd proyecto1_arquitecturaDeNube/Implementacion_Nube


### 2. Iniciar Contenedores
bash
docker-compose up --build --force-recreate


---

## 🔧 Configuración del Peer #1

### Acceder al Contenedor
bash
docker exec -it peer1 bash


### Configurar Entorno Virtual
bash
python3.11 -m venv ~/venv311
source ~/venv311/bin/activate
pip install -r requirements.txt
cd peer1/client/__pycache__/


---

## 📡 Comandos Disponibles

> *Nota:* Todos los comandos se ejecutan con (venv) activo

### 🌐 Gestión de Red
bash
# Listar la red de peers
python main.py --host 172.31.22.148 --port 5001 --action network_list

# Ver estado del peer
python main.py --host 172.31.22.148 --port 5001 --action status

# Agregar nuevo peer
python main.py --host 172.31.22.148 --port 5001 --action add_peer \
  --peer_name peer2 \
  --peer_url https://172.31.22.148:5002/ \
  --peer_grpc 172.31.22.148:50054


### 📁 Gestión de Archivos
bash
# Listar archivos disponibles
python main.py --host 172.31.22.148 --port 5001 --action list

# Localizar archivo en la red
python main.py --host 172.31.22.148 --port 5001 --action locate \
  --filename ejemplo.txt

# Descargar archivo (gRPC)
python main.py --host 172.31.22.148 --port 5001 --action download_grpc \
  --filename ejemplo.txt

# Subir archivo (gRPC)
python main.py --host 172.31.22.148 --port 5001 --action upload_grpc \
  --filepath /ruta/al/archivo.txt


---

## 📝 Estructura de Comandos

| Acción | Parámetros Requeridos | Descripción |
|--------|----------------------|-------------|
| network_list | - | Lista todos los peers conectados |
| status | - | Muestra el estado actual del peer |
| list | - | Lista archivos disponibles |
| locate | --filename | Busca un archivo específico |
| download_grpc | --filename | Descarga archivo via gRPC |
| upload_grpc | --filepath | Sube archivo via gRPC |
| add_peer | --peer_name, --peer_url, --peer_grpc | Añade nuevo peer |

---

## 🎯 Autoevaluacion

Consideramos que logramos apropiarnos del tema, ya que partimos desde la teoría para luego llevarla a la práctica mediante la implementación de un servicio completo de peer-to-peer. Además, la forma organizada en la que desarrollamos el trabajo nos permite afirmar que cumplimos satisfactoriamente con el 100% de los objetivos planteados.


---

## 🧪 Pruebas realizadas
- ✅ **Localhost**: pruebas con múltiples peers y concurrencia.  
- ✅ **Docker**: despliegue en contenedores.  
- ✅ **AWS Academy**: pruebas distribuidas con ≥ 3 peers.  
- ✅ **Manejo de fallos**: la red sigue funcionando si un peer cae.  

---

## 📑 Entregables
- 📄 [Informe técnico en PDF](#)  
- 💻 [Repositorio en GitHub](#)  
- 🎥 [Video demostración (10–15 min)](#)  

---

## 👥 Integrantes
- 👩‍💻 **Daniel Cardona Gonzalez** → Diseño de arquitectura y APIs.  
- 👨‍💻 **Juan José Tamayo Ospina** → Implementación núcleo y concurrencia.  
- 👨‍💻 **María Lucía Cadavid Martínez** → Cliente, despliegue y pruebas en AWS.  

---

<p align="center">
  ✨ Proyecto académico desarrollado para la asignatura <b>Arquitecturas de Nube y Sistemas Distribuidos</b> – UPB, 2025 ✨
</p>
