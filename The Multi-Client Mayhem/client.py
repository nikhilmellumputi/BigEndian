import socket
import hashlib
import os

# Constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
CHUNK_SIZE = 1024  # 1 KB
CLIENT_FOLDER = "received"  # Folder to store received files

def calculate_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def upload_file(file_path, client_id):
    """Upload a file to the server and receive it back with verification."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Client {client_id} connected to server at {SERVER_IP}:{SERVER_PORT}")
        
        # Send the file to the server
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                client_socket.send(chunk)
        client_socket.shutdown(socket.SHUT_WR)  # Signal end of file upload
        print(f"Client {client_id} finished uploading file {file_path}")
        
        # Receive the checksum
        received_checksum = client_socket.recv(64).decode()
        print(f"Client {client_id} received checksum: {received_checksum}")
        
        # Receive and reassemble the file
        file_chunks = {}
        while True:
            try:
                # Receive the chunk header (12 bytes)
                chunk_header = client_socket.recv(12)
                if not chunk_header:
                    break  # End of transmission
                
                # Parse the chunk header as bytes
                client_id_received = int.from_bytes(chunk_header[:4], byteorder='big')
                seq_num = int.from_bytes(chunk_header[4:8], byteorder='big')
                chunk_size = int.from_bytes(chunk_header[8:12], byteorder='big')
                
                # Receive the chunk data
                chunk_data = client_socket.recv(chunk_size)
                if client_id_received == client_id:
                    file_chunks[seq_num] = chunk_data
                    print(f"Client {client_id} received chunk {seq_num} of size {chunk_size}")
            except Exception as e:
                print(f"Client {client_id}: Error parsing chunk header - {e}")
                continue  # Skip invalid chunk and continue
        
        # Check if any chunks were received
        if not file_chunks:
            print(f"Client {client_id}: No chunks received from the server.")
            return
        
        # Check for missing chunks and request retransmission
        missing_chunks = set(range(max(file_chunks.keys()) + 1)) - set(file_chunks.keys())
        for seq_num in missing_chunks:
            try:
                request = client_id.to_bytes(4, byteorder='big') + seq_num.to_bytes(4, byteorder='big')
                client_socket.send(request)
                chunk_header = client_socket.recv(12)
                if chunk_header:
                    chunk_size = int.from_bytes(chunk_header[8:12], byteorder='big')
                    chunk_data = client_socket.recv(chunk_size)
                    file_chunks[seq_num] = chunk_data
                    print(f"Client {client_id} received missing chunk {seq_num}")
            except Exception as e:
                print(f"Client {client_id}: Error handling retransmission - {e}")
                continue
        
        # Reassemble the file
        if not os.path.exists(CLIENT_FOLDER):
            os.makedirs(CLIENT_FOLDER)
        received_file_path = os.path.join(CLIENT_FOLDER, f"received_file_{client_id}.txt")
        with open(received_file_path, "wb") as f:
            for seq_num in sorted(file_chunks.keys()):
                f.write(file_chunks[seq_num])
        
        # Verify the checksum
        calculated_checksum = calculate_checksum(received_file_path)
        if calculated_checksum == received_checksum:
            print(f"Client {client_id}: Transfer Successful")
        else:
            print(f"Client {client_id}: Transfer Failed - Checksum Mismatch")
        
    except Exception as e:
        print(f"Client {client_id}: Error - {e}")
    finally:
        client_socket.close()
        print(f"Client {client_id} disconnected.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python client.py <file_path> <client_id>")
        sys.exit(1)
    file_path = sys.argv[1]
    client_id = int(sys.argv[2])
    upload_file(file_path, client_id)