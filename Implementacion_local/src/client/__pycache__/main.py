import requests
import argparse

def check_status(host: str, port: int):
    """Verifica que el peer esté activo."""
    try:
        url = f"http://{host}:{port}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("✅ Peer activo:", data)
    except Exception as e:
        print("❌ Error al verificar estado:", e)


def list_files(host: str, port: int):
    """Lista los archivos disponibles en el peer."""
    try:
        url = f"http://{host}:{port}/files"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Archivos en '{data.get('directory')}':")
        for file in data.get("files", []):
            print(f"- {file}")
    except Exception as e:
        print("❌ Error al listar archivos:", e)


def locate_file(host: str, port: int, filename: str):
    """Busca un archivo en el peer."""
    try:
        url = f"http://{host}:{port}/locate"
        response = requests.get(url, params={"filename": filename})
        response.raise_for_status()
        data = response.json()
        if data["found"]:
            print(f"✅ Archivo encontrado: {data['filename']}")
            print(f"URL de descarga: {data['download_url']}")
        else:
            print(f"❌ El archivo '{filename}' no está en este peer.")
    except Exception as e:
        print("❌ Error al localizar archivo:", e)


def download_file(host: str, port: int, filename: str):
    """Descarga un archivo desde el peer."""
    try:
        url = f"http://{host}:{port}/download/{filename}"
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Archivo '{filename}' descargado con éxito.")
        else:
            print("❌ Error: archivo no encontrado en el peer.")
    except Exception as e:
        print("❌ Error al descargar archivo:", e)


def upload_file(host: str, port: int, filepath: str):
    """Sube un archivo al peer."""
    try:
        url = f"http://{host}:{port}/upload"
        with open(filepath, "rb") as f:
            files = {"file": (filepath, f)}
            response = requests.post(url, files=files)
        response.raise_for_status()
        data = response.json()
        print("✅ Respuesta del peer:", data)
    except Exception as e:
        print("❌ Error al subir archivo:", e)


if _name_ == "_main_":
    parser = argparse.ArgumentParser(description="Cliente CLI para interactuar con un peer P2P.")
    parser.add_argument("--host", default="127.0.0.1", help="IP del peer.")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del peer.")
    parser.add_argument("--action", required=True, choices=["status", "list", "locate", "download", "upload"],
                        help="Acción a realizar.")
    parser.add_argument("--filename", help="Nombre del archivo para locate/download.")
    parser.add_argument("--filepath", help="Ruta del archivo para upload.")

    args = parser.parse_args()

    if args.action == "status":
        check_status(args.host, args.port)
    elif args.action == "list":
        list_files(args.host, args.port)
    elif args.action == "locate":
        if not args.filename:
            print("⚠️ Debes indicar --filename para locate")
        else:
            locate_file(args.host, args.port, args.filename)
    elif args.action == "download":
        if not args.filename:
            print("⚠️ Debes indicar --filename para download")
        else:
            download_file(args.host, args.port, args.filename)
    elif args.action == "upload":
        if not args.filepath:
            print("⚠️ Debes indicar --filepath para upload")
        else:
            upload_file(args.host, args.port, args.filepath)