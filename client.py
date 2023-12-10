import pyfiglet
import socket
import hashlib

from datetime import datetime
from threading import Thread


def listen_for_messages():
    while True:
        received_data = server.recv(1024).decode()
        received_hash = server.recv(1024).decode()
        sender, message = received_data.split(separator_token)
        checked_hash = hashlib.sha512(message.encode()).hexdigest()
        if received_hash != checked_hash:
            print("This message was tampered!!")
        else:
            date_received = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{sender}] : {message}")
            print(f"received: {date_received}")


HOST = '127.0.0.1'
PORT = 5002
SERVER_ADDR = (HOST, PORT)
separator_token = "<SEP>"

# create socket to connect to server
server = socket.socket()
try:
    print("\nEstablishing connection to chat server")
    server.connect(SERVER_ADDR)
    print("Connection successful!")
except socket.error as e:
    print(f"Error connecting to server: {e}")
    print("""\n###############################################################
##                                                           ##
##    	          !! Server may be down !!                   ##
##            Contact your system administrator              ##
##                                                           ##
###############################################################\n""")
    exit(1)


ascii_banner = pyfiglet.figlet_format("python chat app")
print(ascii_banner)

while True:
    print("\n-----------------------")
    print(":: Client Main Menu ::")
    print("-----------------------")
    print("1. Login")
    print("2. Request to Register")
    print("3. Exit")

    menu_option = input("Enter your choice (1/2/3):")

    if menu_option == '1':
        username = input("Enter your username: ")
        password = input("Enter your password: ")  # prompt the client for a username and password
        # send the username and password with separator
        credentials = f"{username}{separator_token}{password}"
        server.sendall(credentials.encode())

        response = server.recv(1024).decode()  # receive response from the server
        print("\n" + response)
        if response != 'Authentication successful!':
            exit(0)

        listen_thread = Thread(target=listen_for_messages)
        listen_thread.daemon = True
        listen_thread.start()

        print("\nYou are now logged in!")
        print("Enter your messages below:")
        while True:
            # user inputs a message
            outgoing_message = input("\n")
            if outgoing_message.lower() == 'exit':
                break
            # create hash of message
            outgoing_message_hash = hashlib.sha512(outgoing_message.encode()).hexdigest()
            # # send username, message, and hash of message
            # outgoing_message = f"{username}{separator_token}{outgoing_message}{separator_token}{outgoing_message_hash}"
            outgoing_message = f"{username}{separator_token}{outgoing_message}"
            server.sendall(outgoing_message.encode())
            server.sendall(outgoing_message_hash.encode())

            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"sent: {date_now}")
            print("")

        server.close()
    elif menu_option == '2':
        user_registration()
    elif menu_option == '3':
        print("Exiting... Goodbye!")
        break
    else:
        print("Invalid option.")
