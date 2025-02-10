# Steps to Test
## Start the Server:
Run the server:
python server.py
## Run Multiple Clients:
Open two terminals and run the clients:
python client.py data/file1.txt 0
python client.py data/file2.txt 1
## Verify Output:
Server logs will show the files being split and chunks being sent.
Client logs will show the chunks being received and reassembled.

## Screenshots of terminals
### Server Side
![server](https://github.com/user-attachments/assets/8b037152-fd03-4561-8745-c571f5115a78)
### Client 1
![client 1](https://github.com/user-attachments/assets/09d6ce3b-9eeb-4ff0-b458-2737fede21d9)
### Client 2
![client 2](https://github.com/user-attachments/assets/3f725f21-f603-477c-89a3-6672e6b2db49)
