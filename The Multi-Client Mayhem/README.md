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
![Alt text](/The Multi-Client Mayhem/ss/server.jpg?raw=true "Server")
