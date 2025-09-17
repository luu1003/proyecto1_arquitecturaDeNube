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

---

## ⚙️ Configuración del Peer
Cada peer usa un archivo `config.json` con:  
- 🌐 **IP** y **puerto** de escucha.  
- 📁 **Directorio** de archivos compartidos.  
- 🤝 **Peer amigo titular** y **suplente**.  

---

## 📂 Estructura del repositorio
# proyecto1_arquitecturaDeNube
│── src/ # Código fuente
│ ├── pservidor/ # Microservicios
│ ├── pcliente/ # Cliente
│ ├── config/ # Archivos de configuración
│── docs/ # Informe técnico y diagramas
│── tests/ # Scripts y casos de prueba
│── docker/ # Configuración Docker
│── README.md # Este archivo


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
- 👨‍💻 **María Lucía Cadavid** → Cliente, despliegue y pruebas en AWS.  

---

<p align="center">
  ✨ Proyecto académico desarrollado para la asignatura <b>Arquitecturas de Nube y Sistemas Distribuidos</b> – UPB, 2025 ✨
</p>
