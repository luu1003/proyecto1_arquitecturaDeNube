import os, json
from concurrent import futures
import grpc
import grpc_pb2
import grpc_pb2_grpc
import requests

# ----------------- Configuración -----------------
def load_config(path: str):
    with open(path, "r") as f:
        return json.load(f)

CONFIG_PATH = os.getenv("CONFIG_PATH", "../server/peer4.json")
config = load_config(CONFIG_PATH)

DIRECTORY = "peer2/server/shared_files_peer2"  # Cambia a tu carpeta de peer
LOCAL_PEER_NAME = "peer2"

# Tabla de archivos conocidos por este peer
peer_files = {
    LOCAL_PEER_NAME: [
        f for f in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, f))
    ]
}

print(peer_files)


class FileServiceServicer(grpc_pb2_grpc.FileServiceServicer):

    def DownloadFile(self, request, context):
        """Envía el archivo en chunks"""

        refresh_peers()

        file_path = os.path.join(DIRECTORY, request.filename)
        if os.path.exists(file_path):
            chunk_size = 1024 * 64  # 64 KB
            chunk_number = 0
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    yield grpc_pb2.FileChunk(
                        filename=request.filename,
                        content=chunk,
                        chunk_number=chunk_number
                    )
                    chunk_number += 1
            return

        # No está local → flooding a otros peers

        for peer in config.get("peers", []):
            try:
                target = f"{peer['ip']}:{peer['port_grpc']}"
                with grpc.insecure_channel(target) as channel:
                    stub = grpc_pb2_grpc.FileServiceStub(channel)
                    response_stream = stub.DownloadFile(
                        grpc_pb2.FileRequest(filename=request.filename),
                        timeout=10
                    )

                    # Proxy: retransmitimos los chunks de ese peer
                    for chunk in response_stream:
                        yield chunk
                    return  
            except Exception as e:
                # Si un peer falla, seguimos probando con el siguiente
                continue

        #  Ningún peer lo tiene
        context.set_details("File not found in network")
        context.set_code(grpc.StatusCode.NOT_FOUND)
        return

    def UploadFile(self, request_iterator, context):
        """Recibe un archivo en chunks y lo guarda en DIRECTORY"""

        refresh_peers()

        filename = None
        try:
            for chunk in request_iterator:
                if filename is None:
                    filename = chunk.filename
                    file_path = os.path.join(DIRECTORY, filename)
                    f = open(file_path, "wb")  # abrir una vez

                f.write(chunk.content)

            if 'f' in locals() and not f.closed:
                f.close()

            # Actualizar peer_files para que aparezca en /files
            if filename and filename not in peer_files[LOCAL_PEER_NAME]:
                peer_files[LOCAL_PEER_NAME].append(filename)

            return grpc_pb2.UploadStatus(success=True, message="Upload complete")

        except Exception as e:
            return grpc_pb2.UploadStatus(success=False, message=str(e))


def refresh_peers():
    """
    Refresca los archivos de todos los peers conocidos.
    """
    # 1. Actualizar archivos locales
    peer_files[LOCAL_PEER_NAME] = [
        f for f in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, f))
    ]

    # 2. Actualizar info de los peers remotos
    for peer in config.get("peers", []):
        try:
            url = f"http://{peer['ip']}:{peer['port_rest']}/files"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                remote_files = resp.json().get("peer_files", {}).get(peer["name"], [])
                peer_files[peer["name"]] = remote_files
        except Exception:
            continue  # ignorar peers que no respondan



# ----------------- Servidor gRPC -----------------
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_pb2_grpc.add_FileServiceServicer_to_server(FileServiceServicer(), server)
    grpc_port = 50050
    server.add_insecure_port(f"[::]:{grpc_port}")
    print(f"gRPC server listening on port {grpc_port}...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
