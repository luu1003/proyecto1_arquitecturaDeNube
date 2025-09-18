import json
import os
from fastapi import FastAPI
from fastapi import Query
from fastapi.responses import FileResponse

# Función para cargar configuración ----------
def load_config(path: str):
    with open(path, "r") as f:
        return json.load(f)

# Cargar configuración ---------

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/peer1.json")
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
def list_files():
    try:
        files = os.listdir(DIRECTORY)
        # Filtrar solo archivos (no carpetas)
        files = [f for f in files if os.path.isfile(os.path.join(DIRECTORY, f))]
        return {"directory": DIRECTORY, "files": files}
    except Exception as e:
        return {"error": str(e)}

# Nuevo endpoint /locate ----------
@app.get("/locate")
def locate_file(filename: str = Query(..., description="Nombre del archivo a buscar")):
    try:
        files = os.listdir(DIRECTORY)
        if filename in files:
            # Construir URL de descarga
            download_url = f"http://{config['ip']}:{config['port_rest']}/download/{filename}"
            return {
                "found": True,
                "filename": filename,
                "download_url": download_url
            }
        else:
            return {"found": False, "filename": filename}
    except Exception as e:
        return {"error": str(e)}