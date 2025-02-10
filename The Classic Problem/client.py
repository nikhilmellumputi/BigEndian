import socket
import hashlib

def calculate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def receive_file(server_ip, server_port, file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    
    # Receive the checksum first
    received_checksum = client_socket.recv(64).decode()
    
    # Receive the file chunks
    file_chunks = {}
    while True:
        chunk_header = client_socket.recv(12)
        if not chunk_header:
            break
        seq_num = int(chunk_header[:4].decode())
        chunk_size = int(chunk_header[4:12].decode())
        chunk_data = client_socket.recv(chunk_size)
        file_chunks[seq_num] = chunk_data
    
    # Reassemble the file
    with open(file_path, "wb") as f:
        for seq_num in sorted(file_chunks.keys()):
            f.write(file_chunks[seq_num])
    
    # Verify the checksum
    calculated_checksum = calculate_checksum(file_path)
    if calculated_checksum == received_checksum:
        print("Transfer Successful")
    else:
        print("Transfer Failed: Checksum mismatch")

if __name__ == "__main__":
    receive_file("127.0.0.1", 12345, "received_data.txt")