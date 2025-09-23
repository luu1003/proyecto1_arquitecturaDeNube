import json
import os
import httpx

from fastapi import FastAPI, Query, UploadFile, File, Body, Response
from fastapi.responses import FileResponse, StreamingResponse

# --------- Función para cargar configuración ----------
def load_config(path: str):
    with open(path, "r") as f:
        return json.load(f)

# --------- Cargar configuración ---------
CONFIG_PATH = os.getenv("CONFIG_PATH", "config/peer1.json")
config = load_config(CONFIG_PATH)

DIRECTORY = config["directory"]
LOCAL_PEER_NAME = config.get("name", "peer1")  # nombre de este peer
LOCAL_PEER_URL = config.get("url", f"http://{config['ip']}:{config['port_rest']}")

# --------- Tabla de archivos por peer ---------
peer_files = {
    LOCAL_PEER_NAME: [
        f for f in os.listdir(DIRECTORY)
        if os.path.isfile(os.path.join(DIRECTORY, f))
    ]
}

# --------- Servidor FastAPI ---------
app = FastAPI()

@app.get("/")
def read_root():
    return {
        "msg": "Peer activo",
        "config": config
    }

# --------- Endpoint /files ----------
@app.get("/files")
async def list_files():
    """Listar los archivos conocidos por cada peer"""
    return {"peer_files": peer_files}

# --------- Endpoint /locate ----------
@app.get("/locate")
async def locate_file(filename: str = Query(...)):
    """
    Localizar un archivo en la red de peers.
    Si está en el peer local, devuelve su propia URL.
    Si está en otro peer, busca la URL en la lista de peers conocidos.
    """
    sources = []

    for peer, files in peer_files.items():
        if filename in files:
            # Archivo en este peer
            if peer == LOCAL_PEER_NAME:
                sources.append({
                    "peer": peer,
                    "download_url": f"{LOCAL_PEER_URL}/download/{filename}"
                })
            # Archivo en peers remotos
            else:
                for p in config.get("peers", []):
                    if p.get("name") == peer:
                        sources.append({
                            "peer": peer,
                            "download_url": f"{p['url']}/download/{filename}"
                        })

    if sources:
        return {
            "found": True,
            "filename": filename,
            "sources": sources
        }

    return {"found": False, "filename": filename}

# --------- Endpoint /download ----------
@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Descargar un archivo.
    Primero lo localiza en la red y luego lo descarga desde la URL obtenida.
    """
    location_data = await locate_file(filename)

    if not location_data.get("found"):
        return Response(content=json.dumps({"error": "Archivo no encontrado"}), status_code=404, media_type="application/json")

    # Tomar la primera fuente disponible
    source = location_data["sources"][0]
    download_url = source["download_url"]

    # Si la URL es local, servir el archivo directamente
    if source["peer"] == LOCAL_PEER_NAME:
        file_path = os.path.join(DIRECTORY, filename)
        if os.path.exists(file_path):
            return FileResponse(file_path, filename=filename)
        else:
            return Response(content=json.dumps({"error": "Archivo no encontrado localmente"}), status_code=404, media_type="application/json")

    # Si es remota, descargar y transmitir usando el generador
    return StreamingResponse(_stream_remote_file(download_url), media_type="text/plain")

# --------- Endpoint /upload ----------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Subir un archivo al peer local.
    Se guarda en el directorio compartido y se registra en peer_files.
    """
    file_path = os.path.join(DIRECTORY, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        if file.filename not in peer_files[LOCAL_PEER_NAME]:
            peer_files[LOCAL_PEER_NAME].append(file.filename)
        return {"status": "ok", "filename": file.filename}
    except Exception as e:
        return {"error": str(e)}

# --------- Endpoint /add_peer ----------
@app.post("/add_peer")
async def add_peer(peer: dict = Body(...)):
    """
    Registrar un peer remoto en la lista de peers conocidos.
    Requiere JSON: {"name": "peer2", "url": "http://127.0.0.1:5002"}
    """
    if "name" not in peer or "url" not in peer:
        return {"error": "El peer debe tener 'name' y 'url'"}
    config.setdefault("peers", [])
    config["peers"].append(peer)
    return {"status": "ok", "peers": config["peers"]}

# --------- Endpoint /add_file ----------
@app.post("/add_file")
async def add_file(data: dict = Body(...)):
    """
    Registrar un archivo en un peer específico (simulación).
    Requiere JSON: {"peer": "peer2", "filename": "video.mp4"}
    """
    peer = data.get("peer")
    filename = data.get("filename")

    if not peer or not filename:
        return {"error": "Se requieren 'peer' y 'filename'"}

    if peer not in peer_files:
        peer_files[peer] = []

    if filename not in peer_files[peer]:
        peer_files[peer].append(filename)
        return {"status": "ok", "peer": peer, "files": peer_files[peer]}
    else:
        return {"status": "ya existe", "peer": peer, "files": peer_files[peer]}

# --------- Endpoint /peers ----------
@app.get("/peers")
async def list_peers():
    """Listar los peers conocidos por este nodo"""
    return {"peers": config.get("peers", [])}

# --------- Helper para streaming ----------
async def _stream_remote_file(url: str):
    """
    Un generador asíncrono para descargar y transmitir un archivo desde una URL.
    Maneja el ciclo de vida del cliente httpx para el streaming.
    """
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url) as r:
                r.raise_for_status()
                async for chunk in r.aiter_bytes():
                    yield chunk
    except httpx.HTTPStatusError as e:
        error_message = json.dumps({"error": f"Failed to download file from peer: {e}"})
        yield error_message.encode('utf-8')
    except Exception as e:
        error_message = json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
        yield error_message.encode('utf-8')