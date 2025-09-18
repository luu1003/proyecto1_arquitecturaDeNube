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

# Servidor FastAPI ---------
app = FastAPI()

@app.get("/")
def read_root():
    return {
        "msg": "Peer activo",
        "config": config
    }
