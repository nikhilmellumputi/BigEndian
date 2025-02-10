import socket
import hashlib
import os

def calculate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def split_file(file_path, chunk_size):
    chunks = {}
    with open(file_path, "rb") as f:
        seq_num = 0
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            chunks[seq_num] = chunk_data
            seq_num += 1
    return chunks

def send_file(server_ip, server_port, file_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)
    
    print("Server listening on {}:{}".format(server_ip, server_port))
    client_socket, client_address = server_socket.accept()
    print("Connected to client:", client_address)
    
    # Calculate and send the checksum
    checksum = calculate_checksum(file_path)
    client_socket.send(checksum.encode())
    
    # Split the file into chunks and send them
    chunk_size = 1024
    file_chunks = split_file(file_path, chunk_size)
    for seq_num, chunk_data in file_chunks.items():
        chunk_header = f"{seq_num:04d}{len(chunk_data):08d}".encode()
        client_socket.send(chunk_header + chunk_data)
    
    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    send_file("127.0.0.1", 12345, "data.txt")