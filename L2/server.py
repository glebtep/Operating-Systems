import socket
import signal
import sys
import json
import threading


listen_address = '127.0.0.1' # i used default one
listen_port = 1111
max_connections = 5
shoplist_items = []

def shoplist(signum, frame):
    with open('shoplist.txt', 'w') as backup_file:
        backup_file.write(json.dumps(shoplist_items))
    print("  Shopping list complete. Server is shutting down.")
    sys.exit(0)


signal.signal(signal.SIGTERM, shoplist)
signal.signal(signal.SIGINT, shoplist)  # For CTRL + C


def client_request(client_socket):
    try:
        # Receive data from client
        request_data = client_socket.recv(1024).decode('utf-8')
        request = json.loads(request_data)
        
        # action <---> response
        action = request.get('action')
        if action == 'add':
            shoplist_items.append(request.get('item'))
            response = "Item added."
        elif action == 'retrieve':
            response = json.dumps(shoplist_items)
        else:
            response = "Unknown action."
        
        client_socket.sendall(response.encode('utf-8'))
    finally:
        client_socket.close()

def client_thread(connection, client_addr):

    print(f"Connected to client: {client_addr}")
    client_request(connection)

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((listen_address, listen_port))
        server_socket.listen(max_connections)
        print("Server is running and listening for connections.")
        
        try:
            while True:
                # Accept new connections (clients)
                client_sock, addr = server_socket.accept()
                # Connection becomes a thread
                threading.Thread(target=client_thread, args=(client_sock, addr)).start()
        except KeyboardInterrupt:

            print("\nServer is shutting down gracefully.")
            sys.exit(0)
