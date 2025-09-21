import requests
import argparse

def list_files(host: str, port: int):
    """
    Connects to a peer and lists its available files.
    """
    try:
        url = f"http://{host}:{port}/files"
        print(f"Attempting to connect to {url}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        print(f"Files available in directory '{data.get('directory')}' on peer {host}:{port}:")
        if data.get("files"):
            for file in data["files"]:
                print(f"- {file}")
        else:
            print("No files found on the peer.")

    except requests.exceptions.ConnectionError:
        print(f"Error: Connection to {host}:{port} refused. Make sure the peer server is running.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI client to interact with a P2P file sharing peer.")
    parser.add_argument("--host", default="127.0.0.1", help="The host IP of the peer to connect to.")
    parser.add_argument("--port", type=int, default=5000, help="The port number of the peer.")

    args = parser.parse_args()

    list_files(args.host, args.port)
