import socket
import hashlib
import os
import threading
import random

# Constants
CHUNK_SIZE = 1024  # 1 KB
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
SERVER_FOLDER = "received"  # Folder to store uploaded files

def calculate_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def split_file(file_path, chunk_size):
    """Split a file into fixed-size chunks and assign sequence numbers."""
    chunks = {}
    with open(file_path, "rb") as f:
        seq_num = 0
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            chunks[seq_num] = chunk_data
            seq_num += 1
    print(f"File split into {len(chunks)} chunks")  # Debug log
    return chunks

def simulate_errors(chunk_data):
    """Simulate packet corruption or drop with a 10% probability."""
    if random.random() < 0.1:  # 10% chance of error
        if random.random() < 0.5:  # 50% chance of corruption
            # Corrupt the chunk by flipping some bits
            chunk_data = bytearray(chunk_data)
            for i in range(min(10, len(chunk_data))):
                chunk_data[i] ^= 0xFF
            return bytes(chunk_data)
        else:
            # Drop the chunk
            return None
    return chunk_data

def handle_client(client_socket, client_id):
    """Handle file upload, splitting, and transmission for a single client."""
    try:
        # Create the server folder if it doesn't exist
        if not os.path.exists(SERVER_FOLDER):
            os.makedirs(SERVER_FOLDER)
        
        # Receive the file from the client
        file_path = os.path.join(SERVER_FOLDER, f"server_file_{client_id}.txt")
        with open(file_path, "wb") as f:
            while True:
                chunk = client_socket.recv(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
        print(f"File received from client {client_id} and saved to {file_path}")
        
        # Split the file into chunks
        file_chunks = split_file(file_path, CHUNK_SIZE)
        
        # Calculate and send the checksum
        checksum = calculate_checksum(file_path)
        client_socket.send(checksum.encode())
        print(f"Checksum sent to client {client_id}: {checksum}")
        
        # Send the chunks with error simulation
        for seq_num, chunk_data in file_chunks.items():
            chunk_data = simulate_errors(chunk_data)  # Enable error simulation
            if chunk_data:
                # Send the chunk header: client_id (4 bytes) + seq_num (4 bytes) + chunk_size (8 bytes)
                chunk_header = client_id.to_bytes(4, byteorder='big') + seq_num.to_bytes(4, byteorder='big') + len(chunk_data).to_bytes(4, byteorder='big')
                client_socket.send(chunk_header)
                client_socket.send(chunk_data)
                print(f"Sent chunk {seq_num} to client {client_id}")
        
        # Handle retransmission requests
        while True:
            request = client_socket.recv(12).decode()
            if not request:
                break
            client_id_requested = int(request[:4])
            seq_num_requested = int(request[4:8])
            if client_id_requested == client_id and seq_num_requested in file_chunks:
                chunk_data = file_chunks[seq_num_requested]
                chunk_header = f"{client_id:04d}{seq_num_requested:04d}{len(chunk_data):08d}".encode()
                client_socket.send(chunk_header + chunk_data)
                print(f"Resent chunk {seq_num_requested} to client {client_id}")
        
    except Exception as e:
        print(f"Error handling client {client_id}: {e}")
    finally:
        client_socket.close()
        print(f"Client {client_id} disconnected.")

def start_server():
    """Start the server and listen for incoming connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow reusing the socket address
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    
    client_id = 0
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected to client {client_id} at {client_address}")
        threading.Thread(target=handle_client, args=(client_socket, client_id)).start()
        client_id += 1

if __name__ == "__main__":
    start_server()