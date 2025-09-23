import os
from concurrent import futures
import grpc
import grpc_pb2
import grpc_pb2_grpc

# ----------------- Configuración -----------------
DIRECTORY = "peer3/server/shared_files_peer3"  # Cambia a tu carpeta de peer
LOCAL_PEER_NAME = "peer3"

# Tabla de archivos conocidos por este peer
peer_files = {
    LOCAL_PEER_NAME: [
        f for f in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, f))
    ]
}

# ----------------- Servicio gRPC -----------------
class FileServiceServicer(grpc_pb2_grpc.FileServiceServicer):

    def DownloadFile(self, request, context):
        """Envía el archivo en chunks"""
        file_path = os.path.join(DIRECTORY, request.filename)
        if not os.path.exists(file_path):
            context.set_details("File not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return

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

    def UploadFile(self, request_iterator, context):
        """Recibe un archivo en chunks y lo guarda en DIRECTORY"""
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
