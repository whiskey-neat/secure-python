import csv
import hashlib
import os
import socket
from threading import Thread
from authentication import check_user_credentials


def process_user_requests():
    # create a list of user requests
    with open("user_credentials_requests.csv", 'r') as requests_file:
        requests_reader = csv.reader(requests_file)
        requests = list(requests_reader)

    if not requests:
        print("\nNo pending user requests.")
        return

    # print pending requests
    print("Pending User Requests:")
    for index, request in enumerate(requests, start=1):
        print(f"{index}. {request}")

    index_option = input("Enter the index number of the quest to accept (0 to cancel): ")
    if index_option == '0':
        return

    try:
        request_index = int(index_option) - 1
        if 0 <= request_index < len(requests):
            user_data = requests.pop(request_index)
            with open('user_credentials.csv', 'a', newline='') as user_credentials_file:
                writer = csv.writer(user_credentials_file)
                writer.writerow(user_data)
            with open('user_credentials_requests.csv', 'w', newline='') as requests_file:
                requests_writer = csv.writer(requests_file)
                requests_writer.writerows(requests)
            print(f"User request {user_data} accepted and added to Databases.")
        else:
            print("Invalid index.")
    except ValueError:
        print("Invalid input. Please enter a valid index.")


def authenticate_user(conn, separator):
    # receive username and password from the client
    credentials = conn.recv(1024).decode('utf-8').strip()

    # split credentials into username and password
    username, password = credentials.split(separator)

    # check if the username and password are correct
    if check_user_credentials(username, password):
        conn.sendall('Authentication successful!'.encode('utf-8'))
        return True
    else:
        print(f"[!] Error: [Authentication FAILED] Reason: Incorrect credentials for username: {username}")
        conn.sendall('Authentication failed.'.encode('utf-8'))
        conn.close()
        return False


def listen_for_messages(conn, addr, clients):
    while True:
        try:
            received_data = conn.recv(1024).decode()  # listen for an incoming message
            received_hash = conn.recv(1024).decode()  # listen for an incoming hash
            print(f"[*] Received message from {addr}")
            username, message = received_data.rsplit(separator_token, 1)
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
                received_data = "Message is tampered!!"

        # iterate over all connected sockets
        for each_client in clients:
            if each_client != conn:
                # send the message and hash to all connected clients except the sender
                each_client.send(received_data.encode())
                each_client.send(received_hash.encode())


def server_creation(server_ip, server_port, server_address):
    # initialise a set of all connected clients
    clients = set()

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(server_address)
    server.listen(20)   # allow 20 connections
    print(f"[Chat Server] Listening as {server_ip}:{server_port}")

    while True:
        try:
            client_conn, client_addr = server.accept()
            print(f"[+] {client_addr} has connected to the server.")

            # Spawn a new thread for each client to handle authentication
            auth = Thread(target=authenticate_user, args=(client_conn, separator_token))
            auth.start()

            clients.add(client_conn)

            # start a new thread that listens for each client's messages
            listen_thread = Thread(target=listen_for_messages, args=(client_conn, client_addr, clients))
            listen_thread.start()

        except Exception as e:
            print(f"[!] Error accepting connection: {e}")

    for client in clients:
        client.close()


def create_an_admin():
    admin_username = input("Enter an admin username: ")

    # if admin credentials file doesn't exist
    if not os.path.isfile("admin_credentials.csv"):
        # create one
        with open("admin_credentials.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Password"])

    with open("admin_credentials.csv", mode='r') as file:
        admin_credentials = csv.reader(file)
        for row in admin_credentials:
            if row and row[0] == admin_username:
                print("Admin already exists!")
                return

    # write admin data to admin_credentials.csv
    with open("admin_credentials.csv", mode='a', newline='') as file:
        admin_password = input("Enter an admin password: ")
        writer = csv.writer(file)
        writer.writerow([admin_username, admin_password])
        print(f"Admin credentials successfully created with username: {admin_username}")


def admin_login():
    while True:
        admin_username = input("\nEnter admin username: ")
        admin_password = input("Enter admin password: ")

        # check if admin_credentials.csv exists
        if not os.path.isfile("admin_credentials.csv"):
            print("No admin accounts!")
            return False

        # validate admin credentials
        with open("admin_credentials.csv", mode='r') as file:
            credentials = csv.reader(file)
            for row in credentials:
                if row and row[0] == admin_username and row[1] == admin_password:
                    print("\nAdmin login successful!")
                    return True
            print("Admin credentials are invalid!")
            return False


def admin_menu():
    while True:
        print("\n-----------------------")
        print(":: Admin Main Menu ::")
        print("-----------------------")
        print("1. Process User Requests")
        print("2. Create a Server")
        print("3. Return to Main Menu")

        admin_option = input("Enter your choice (1/2/3): ")

        if admin_option == '1':
            process_user_requests()
        elif admin_option == '2':
            server_creation(HOST, PORT, SERVER_ADDR)
        elif admin_option == '3':
            print("Returning to main menu")
            break
        else:
            print("Invalid option.")


HOST = '127.0.0.1'
PORT = 5002
SERVER_ADDR = (HOST, PORT)
separator_token = '<SEP>'


while True:
    print("\n-----------------------")
    print(":: Server Main Menu ::")
    print("-----------------------")
    print("1. Create Admin Account")
    print("2. Admin Login")
    print("3. Exit")

    menu_option = input("Enter your choice (1/2/3): ")

    if menu_option == '1':
        create_an_admin()
    elif menu_option == '2':
        if admin_login():
            admin_menu()
    elif menu_option == '3':
        print("Exiting... Goodbye!")
        break
    else:
        print("Invalid option.")
