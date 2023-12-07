import socket
from threading import Thread
import hashlib

from authentication import check_user_credentials


def authenticate_user(conn):
    # receive username and password from the client
    credentials = conn.recv(1024).decode('utf-8').strip()

    # split credentials into username and password
    username, password = credentials.split(separator_token)

    # check if the username and password are correct
    if check_user_credentials(username, password):
        conn.sendall('Authentication successful!'.encode('utf-8'))
        return True
    else:
        print(f"[!] Error: [Authentication FAILED] Reason: Incorrect credentials for username: {username}")
        conn.sendall('Authentication failed.'.encode('utf-8'))
        conn.close()
        return False


def listen_to_client(conn):
    while True:
        try:
            received_data = conn.recv(1024).decode()  # listen for an incoming message
            message, received_hash = received_data.rsplit(separator_token, 1)
        except Exception as e:
            print(f"[!] Error: {e}")
            clients.remove(conn)  # remove client from set
            break
        else:
            # generate hash of the message received
            checked_hash = hashlib.sha512(message.encode()).hexdigest()

            # if the hash of the received message is not equal to the hash of the message sent
            if received_hash != checked_hash:
                print("[-] Message is tampered!!")
                continue

            message = message.replace(separator_token, ": ")

        # iterate over all connected sockets
        for each_client in clients:
            if each_client != conn:
                # send the message
                each_client.send(message.encode())


HOST = "127.0.0.1"  # server IP
PORT = 5002  # server PORT
SERVER_ADDR = (HOST, PORT)
separator_token = "<SEP>"  # separate client name and message

# initialise a set of all connected clients
clients = set()

# create a socket
s = socket.socket()
# make port reusable
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the server
s.bind(SERVER_ADDR)
# set number of allowed  connections
s.listen(5)
print(f"[Chat Application Server] Listening as {HOST}:{PORT}")

while True:
    # we keep listening for new connections all the time
    client_conn, client_address = s.accept()

    auth = Thread(target=authenticate_user, args=(client_conn,))
    auth.start()

    print(f"[+] {client_address} successfully connected.")

    # add the new connected client to connected sockets
    clients.add(client_conn)
    # start a new thread that listens for each client's messages
    t = Thread(target=listen_to_client, args=(client_conn,))
    # make the thread daemon, so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for connection in clients:
    connection.close()

# close server socket
s.close()
