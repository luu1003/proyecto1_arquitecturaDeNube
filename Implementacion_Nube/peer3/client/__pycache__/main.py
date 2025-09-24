import requests
import argparse
import grpc
import os
import grpc_pb2
import grpc_pb2_grpc

# ----------------- HTTP Functions -----------------
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


def list_files(host: str, port: int, network=False):
    """Lista archivos locales o de toda la red."""
    try:
        endpoint = "/network_files" if network else "/files"
        url = f"http://{host}:{port}{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("Archivos por peer:")
        for peer, files in data.get("peer_files", {}).items():
            print(f"- {peer}:")
            for f in files:
                print(f"    {f}")
    except Exception as e:
        print("❌ Error al listar archivos:", e)


def locate_file(host: str, port: int, filename: str):
    """Busca un archivo en el peer y obtiene info gRPC si está disponible."""
    try:
        url = f"http://{host}:{port}/locate"
        response = requests.get(url, params={"filename": filename})
        response.raise_for_status()
        data = response.json()
        if data["found"]:
            print(f"✅ Archivo encontrado: {data['filename']}")
            for s in data.get("sources", []):
                print(f"Peer: {s['peer']}")
                print(f"  URL HTTP: {s.get('download_url')}")
                if "grpc" in s:
                    print(f"  gRPC: {s['grpc']}")
        else:
            print(f"❌ El archivo '{filename}' no está en este peer.")
    except Exception as e:
        print("❌ Error al localizar archivo:", e)


# ----------------- HTTP File Transfer -----------------
def download_file_http(host: str, port: int, filename: str):
    """Descarga un archivo usando HTTP."""
    try:
        url = f"http://{host}:{port}/download/{filename}"
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Archivo '{filename}' descargado con éxito por HTTP.")
        else:
            print("❌ Error: archivo no encontrado en el peer.")
    except Exception as e:
        print("❌ Error al descargar archivo:", e)


def upload_file_http(host: str, port: int, filepath: str):
    """Sube un archivo usando HTTP."""
    try:
        url = f"http://{host}:{port}/upload"
        with open(filepath, "rb") as f:
            files = {"file": (os.path.basename(filepath), f)}
            response = requests.post(url, files=files)
        response.raise_for_status()
        data = response.json()
        print("✅ Respuesta del peer:", data)
    except Exception as e:
        print("❌ Error al subir archivo:", e)


# ----------------- gRPC File Transfer -----------------
def download_file_grpc(peer_host, peer_port, filename, save_dir="../../../shared_files_peer3"):
    """Descarga un archivo usando gRPC en chunks."""
    os.makedirs(save_dir, exist_ok=True)
    channel = grpc.insecure_channel(f"{peer_host}:{peer_port}")
    stub = grpc_pb2_grpc.FileServiceStub(channel)
    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as f:
        for chunk in stub.DownloadFile(grpc_pb2.FileRequest(filename=filename)):
            f.write(chunk.content)
    print(f"✅ Archivo '{filename}' descargado con éxito vía gRPC.")


def upload_file_grpc(peer_host, peer_port, filepath):
    """Sube un archivo usando gRPC en chunks."""
    channel = grpc.insecure_channel(f"{peer_host}:{peer_port}")
    stub = grpc_pb2_grpc.FileServiceStub(channel)
    filename = os.path.basename(filepath)

    def file_chunks():
        chunk_size = 1024 * 64
        with open(filepath, "rb") as f:
            chunk_number = 0
            while chunk := f.read(chunk_size):
                yield grpc_pb2.FileChunk(
                    filename=filename,
                    content=chunk,
                    chunk_number=chunk_number
                )
                chunk_number += 1

    response = stub.UploadFile(file_chunks())
    print(f"✅ Subida vía gRPC -> {response.message}")


# ----------------- Peer Management -----------------
def add_peer(host: str, port: int, peer_name: str, peer_url: str, peer_grcp: str):
    """Agrega un peer a la red local o al peer central."""
    try:
        url = f"http://{host}:{port}/add_peer"
        payload = {
            "name": peer_name,
            "url": peer_url,
            "url_grpc": peer_grcp
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Peer '{peer_name}' agregado correctamente:", data)
    except Exception as e:
        print("❌ Error al agregar peer:", e)

# ----------------- CLI -----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente CLI para interactuar con un peer P2P.")
    parser.add_argument("--host", default="127.0.0.1", help="IP del peer.")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del peer.")
    parser.add_argument("--action", required=True,
                        choices=["status", "list", "network_list", "locate", "download_http", "download_grpc",
                                "upload_http", "upload_grpc", "add_peer"],  
                        help="Acción a realizar.")
    parser.add_argument("--filename", help="Nombre del archivo para locate/download.")
    parser.add_argument("--filepath", help="Ruta del archivo para upload.")
    parser.add_argument("--grpc_port", type=int, default=50051, help="Puerto gRPC del peer.")
    parser.add_argument("--peer_name", help="Nombre del peer a agregar.")
    parser.add_argument("--peer_url", help="IP del peer a agregar.")
    parser.add_argument("--peer_grpc", help="Puerto del peer a agregar.")

    args = parser.parse_args()

    if args.action == "status":
        check_status(args.host, args.port)
    elif args.action == "list":
        list_files(args.host, args.port)
    elif args.action == "network_list":
        list_files(args.host, args.port, network=True)
    elif args.action == "locate":
        if not args.filename:
            print("⚠️ Debes indicar --filename para locate")
        else:
            locate_file(args.host, args.port, args.filename)
    elif args.action == "add_peer":
        if not args.peer_name or not args.peer_url or not args.peer_grpc:
            print("⚠️ Debes indicar --peer_name, --peer_host y --peer_port para agregar un peer")
        else:
            add_peer(args.host, args.port, args.peer_name, args.peer_host, args.peer_port)
    elif args.action == "download_http":
        if not args.filename:
            print("⚠️ Debes indicar --filename para download_http")
        else:
            download_file_http(args.host, args.port, args.filename)
    elif args.action == "download_grpc":
        if not args.filename:
            print("⚠️ Debes indicar --filename para download_grpc")
        else:
            download_file_grpc(args.host, args.grpc_port, args.filename)
    elif args.action == "upload_http":
        if not args.filepath:
            print("⚠️ Debes indicar --filepath para upload_http")
        else:
            upload_file_http(args.host, args.port, args.filepath)
    elif args.action == "upload_grpc":
        if not args.filepath:
            print("⚠️ Debes indicar --filepath para upload_grpc")
        else:
            upload_file_grpc(args.host, args.grpc_port, args.filepath)
    