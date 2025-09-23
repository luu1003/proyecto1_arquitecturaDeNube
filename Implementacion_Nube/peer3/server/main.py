import json
import os
import httpx
from fastapi import FastAPI, Query, UploadFile, File, Body
from fastapi.responses import FileResponse

# --------- Función para cargar configuración ----------
def load_config(path: str):
    with open(path, "r") as f:
        return json.load(f)

# --------- Cargar configuración ---------
CONFIG_PATH = os.getenv("CONFIG_PATH", "peer3.json")
config = load_config(CONFIG_PATH)

DIRECTORY = config["directory"]
LOCAL_PEER_NAME = config.get("name", "peer3")
LOCAL_PEER_URL = config.get("url", f"http://{config['ip']}:{config['port_rest']}")

# --------- Tabla de archivos por peer (solo local inicialmente) ---------
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
    Consulta a todos los peers para ver quién tiene el archivo.
    """
    sources = []

    # Revisar peer local
    if filename in peer_files[LOCAL_PEER_NAME]:
        sources.append({
            "peer": LOCAL_PEER_NAME,
            "download_url": f"{LOCAL_PEER_URL}/download/{filename}"
        })

    # Revisar peers remotos
    for p in config.get("peers", []):
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{p['url']}/files")
                resp.raise_for_status()
                remote_files = resp.json().get("peer_files", {}).get(p["name"], [])
                if filename in remote_files:
                    sources.append({
                        "peer": p["name"],
                        "download_url": f"{p['url']}/download/{filename}"
                    })
        except Exception as e:
            # Ignorar peers que no respondan
            continue

    if sources:
        return {"found": True, "filename": filename, "sources": sources}
    else:
        return {"found": False, "filename": filename}

# --------- Endpoint /download ----------
@app.get("/download/{filename}")
async def download_file(filename: str):
    """Descargar un archivo desde este peer"""
    file_path = os.path.join(DIRECTORY, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return {"error": "File not found"}

# --------- Endpoint /upload ----------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Subir un archivo al peer local"""
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
    """Registrar un peer remoto en la lista de peers conocidos"""
    if "name" not in peer or "url" not in peer:
        return {"error": "El peer debe tener 'name' y 'url'"}
    config.setdefault("peers", [])
    config["peers"].append(peer)
    return {"status": "ok", "peers": config["peers"]}

# --------- Endpoint /add_file ----------
@app.post("/add_file")
async def add_file(data: dict = Body(...)):
    """Registrar un archivo en un peer específico (simulación)"""
    peer = data.get("peer")
    filename = data.get("filename")
    if not peer or not filename:
        return {"error": "Se requieren 'peer' y 'filename'"}
    peer_files.setdefault(peer, [])
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

# ------------------------------------

@app.get("/network_files")
async def list_network_files():
    """
    Listar todos los archivos disponibles en la red,
    incluyendo los archivos de todos los peers remotos.
    """
    network_files = {LOCAL_PEER_NAME: peer_files[LOCAL_PEER_NAME].copy()}

    for p in config.get("peers", []):
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{p['url']}/files")
                resp.raise_for_status()
                remote_files = resp.json().get("peer_files", {}).get(p["name"], [])
                network_files[p["name"]] = remote_files
        except Exception:
            # Ignorar peers que no respondan
            continue

    return {"peer_files": network_files}