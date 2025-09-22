import json
import os
from fastapi import FastAPI
from fastapi import Query
from fastapi.responses import FileResponse
from fastapi import UploadFile, File

# Función para cargar configuración ----------
def load_config(path: str):
    with open(path, "r") as f:
        return json.load(f)

# Cargar configuración ---------

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/peer2.json")
config = load_config(CONFIG_PATH)

DIRECTORY = config["directory"]

# Servidor FastAPI ---------
app = FastAPI()

@app.get("/")
def read_root():
    return {
        "msg": "Peer activo",
        "config": config
    }


# endpoint /files ----------
@app.get("/files")
async def list_files():
    files = os.listdir(DIRECTORY)
    files = [f for f in files if os.path.isfile(os.path.join(DIRECTORY, f))]
    return {"directory": DIRECTORY, "files": files}

# endpoint /locate ----------
@app.get("/locate")
async def locate_file(filename: str = Query(...)):
    files = os.listdir(DIRECTORY)
    if filename in files:
        download_url = f"http://{config['ip']}:{config['port_rest']}/download/{filename}"
        return {"found": True, "filename": filename, "download_url": download_url}
    return {"found": False, "filename": filename}

# Correcion al commit anterior, esta funcion realmente funciona y descarga los archvios   

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(DIRECTORY, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return {"error": "File not found"}

# Se agrega un metodo para subir un archivo a un peer

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(DIRECTORY, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        return {"status": "ok", "filename": file.filename}
    except Exception as e:
        return {"error": str(e)}