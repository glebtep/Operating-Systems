import socket
import json


server_address = '127.0.0.1' # i used default one
server_port = 1111

# sends requests to a server and returns response from server
def sendreq_server(action, item=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((server_address, server_port))
            request_data = json.dumps({'action': action, 'item': item})
            sock.sendall(request_data.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            return response
    except ConnectionError:
        return "Connection to the server. Status: FAILED."

#How it runs client app
def main():
    while True:
        print("\n1) Add item\n2) Retrieve items\n3) Exit")
        userchoice = input("What do you want to do? ")
        if userchoice == '1':
            item_to_add = input("What item do you want to add? ")
            print("Server replied:", sendreq_server('add', item_to_add))
        elif userchoice == '2':
            print("Server replied:", sendreq_server('retrieve'))
        elif userchoice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
    main()
