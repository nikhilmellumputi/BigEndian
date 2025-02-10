import socket
import hashlib
import json
import os

CHUNK_SIZE = 1024  # 1 KB per chunk

def compute_checksum(data):
    return hashlib.md5(data).hexdigest()

def send_file_metadata(client, filename):
    total_chunks = os.path.getsize(filename) // CHUNK_SIZE + 1
    metadata = json.dumps({"filename": filename, "total_chunks": total_chunks})
    client.sendall(metadata.encode())
    return total_chunks

def receive_file(client, filename, total_chunks):
    received_chunks = {}
    with open(f"received_{filename}", "wb") as f:
        for i in range(total_chunks):
            data = client.recv(CHUNK_SIZE + 32)  # Receive chunk + checksum
            chunk, checksum = data[:-32], data[-32:].decode()
            received_checksum = compute_checksum(chunk)

            print(f"Received chunk {i} (Expected: {checksum}, Computed: {received_checksum})")

            if received_checksum != checksum:
                print(f"Chunk {i} corrupted. Requesting retransmission.")
                client.sendall(f"RESEND {i}".encode())
                data = client.recv(CHUNK_SIZE + 32)
                chunk, checksum = data[:-32], data[-32:].decode()
                received_checksum = compute_checksum(chunk)
                print(f"Retransmitted chunk {i} (Expected: {checksum}, Computed: {received_checksum})")

            received_chunks[i] = chunk
            f.write(chunk)

    return received_chunks

def start_client(filename, server_host="127.0.0.1", server_port=5000):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_host, server_port))
    
    total_chunks = send_file_metadata(client, filename)
    received_chunks = receive_file(client, filename, total_chunks)
    
    if len(received_chunks) == total_chunks:
        print(f"Client: Transfer Successful for {filename}")
    else:
        print(f"Client: Transfer Failed for {filename}")
    
    client.close()

if __name__ == "__main__":
    filename = input("Enter filename to send: ")
    start_client(filename)
