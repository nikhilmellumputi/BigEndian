import socket
import threading
import os
import hashlib
import json

CHUNK_SIZE = 1024  # 1 KB per chunk

def compute_checksum(data):
    return hashlib.md5(data).hexdigest()

def handle_client(conn, addr):
    print(f"Client {addr} connected.")
    
    # Receive metadata
    metadata = conn.recv(1024).decode()
    file_info = json.loads(metadata)
    filename = file_info["filename"]
    total_chunks = file_info["total_chunks"]
    
    print(f"Receiving {filename} ({total_chunks} chunks) from {addr}")

    # Send chunks
    with open(filename, "rb") as f:
        for i in range(total_chunks):
            chunk = f.read(CHUNK_SIZE)
            checksum = compute_checksum(chunk)
            conn.sendall(chunk + checksum.encode())  # Send chunk + checksum
            print(f"Sent chunk {i} (Checksum: {checksum}) to {addr}")

    print(f"File {filename} sent to {addr}")

    # Handle retransmission requests
    while True:
        try:
            request = conn.recv(1024).decode()
            if not request:
                break
            if request.startswith("RESEND"):
                _, chunk_num = request.split()
                chunk_num = int(chunk_num)
                f.seek(chunk_num * CHUNK_SIZE)
                chunk = f.read(CHUNK_SIZE)
                checksum = compute_checksum(chunk)
                conn.sendall(chunk + checksum.encode())  
                print(f"Resent chunk {chunk_num} (Checksum: {checksum}) to {addr}")
        except:
            break

    conn.close()
    print(f"Client {addr} disconnected.")

def start_server(host="127.0.0.1", port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
