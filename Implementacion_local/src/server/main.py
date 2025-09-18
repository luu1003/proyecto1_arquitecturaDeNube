import json
import os
from fastapi import FastAPI

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


# Nuevo endpoint /files ----------
@app.get("/files")
def list_files():
    try:
        files = os.listdir(DIRECTORY)
        # Filtrar solo archivos (no carpetas)
        files = [f for f in files if os.path.isfile(os.path.join(DIRECTORY, f))]
        return {"directory": DIRECTORY, "files": files}
    except Exception as e:
        return {"error": str(e)}