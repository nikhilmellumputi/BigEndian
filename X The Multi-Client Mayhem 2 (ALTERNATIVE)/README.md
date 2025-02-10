# How It Works
Server listens for incoming connections.
Client connects, sends metadata, and starts receiving chunks.
Each chunk has a checksum to detect corruption.
If corruption is detected, the client requests a retransmission.
Once all chunks are received and verified, the file is reassembled, and "Transfer Successful" is printed.
# Example Usage
## Start the server:
python server.py
## Start two clients (in different terminals):
python client.py
Enter data1.txt in one and data2.txt in the other.
## The clients will receive and verify the file, ensuring no data loss.

## Screenshots
### Server
![server](https://github.com/user-attachments/assets/9fe7f387-7e8a-4180-9c2b-f12693f836eb)
### Client 1
![client1](https://github.com/user-attachments/assets/f3dce53b-844c-4a68-93a0-1f97a845ed54)
### Client 2
![client2](https://github.com/user-attachments/assets/d122db2a-cd2c-480e-ae4c-ba986964376b)
