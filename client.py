import socket
from threading import Thread
from datetime import datetime


def listen_for_messages():
    while True:
        message = server.recv(1024).decode()
        print("\n" + message)


HOST = "127.0.0.1"          # server IP
PORT = 5002                 # server PORT
SERVER_ADDR = (HOST, PORT)  # server ADDRESS
separator_token = "<SEP>"

# create a socket
server = socket.socket()
print(f"[Client] Connecting to {HOST}:{PORT}...")

# connect to the server
server.connect(SERVER_ADDR)
print("[Client] Connection Successful!.\n")

username = input("Enter your username: ")
password = input("Enter your password: ")   # prompt the client for a username and password
# send the username and password with separator
credentials = f"{username}{separator_token}{password}"
server.sendall(credentials.encode())

response = server.recv(1024).decode()   # receive response from the server
print(response)
if response != 'Authentication successful!':
    exit(0)

# prompt the client for a name
name = input("Enter your name: ")
print("")

# thread to listen for messages
t = Thread(target=listen_for_messages)
# thread ends with main thread
t.daemon = True
# start the thread
t.start()

while True:
    # input message we want to send to the server
    outgoing_message = input("")
    if outgoing_message.lower() == 'q':
        break
    # add the datetime and name to the message
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    outgoing_message = f"received: {date_now}\n{name}{separator_token}{outgoing_message}\n"
    # send the message
    server.send(outgoing_message.encode())
    print(f"sent: {date_now}\n")

# close the socket
server.close()