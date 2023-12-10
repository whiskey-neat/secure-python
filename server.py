import csv
import hashlib
import os
import socket
from threading import Thread
from authentication import check_user_credentials
from authentication import hash_and_salt


def process_user_requests():
    # create a list of user requests
    with open("user_credentials_requests.csv", 'r') as requests_file:
        requests_reader = csv.reader(requests_file)
        # create a list of all requests
        requests = list(requests_reader)

    while True:
        if not requests:
            print("\nNo pending user requests.")
            return

        print(f"\n{'>>> Pending User Requests <<<':^40}")
        print("-" * 40)
        print(f"  {'Index': <10} {'Username': <30}")

        for index, request in enumerate(requests, start=1):
            username = request[0]
            print("  {:^5}      {:<30}".format(index, username))

        print("-" * 40)

        index_option = input("\nEnter the index number of the request to process (0 to cancel): ")
        if index_option == '0':
            return

        try:
            request_index = int(index_option) - 1
            if 0 <= request_index < len(requests):
                user_data = requests[request_index]

                action = input(f"\nDo you want to accept the request from username: {user_data[0]} (y/n): ").lower()

                if action == 'y':
                    with open('user_credentials.csv', 'a', newline='') as user_credentials_file:
                        writer = csv.writer(user_credentials_file)
                        writer.writerow(user_data)
                    print(f"User request {user_data[0]} successfully accepted!")
                elif action == 'n':
                    print(f"User request for {user_data[0]} rejected.")
                else:
                    print("Invalid option. Enter 'y' or 'n'")

                requests.pop(request_index)
                with open('user_credentials_requests.csv', 'w', newline='') as requests_file:
                    requests_writer = csv.writer(requests_file)
                    requests_writer.writerows(requests)
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


def register_user(conn, separator):
    try:
        # receive username and password from the client
        credentials = conn.recv(1024).decode('utf-8').strip()

        # split credentials into username and password
        username, password = credentials.split(separator)

        # create a list of existing user credentials
        with open("user_credentials.csv", 'r') as user_credentials_file:
            user_credentials_reader = csv.reader(user_credentials_file)
            user_credentials = list(user_credentials_reader)

        # check if the username is already taken by registered user
        for user in user_credentials:
            if user and user[0] == username:
                conn.sendall('Username is already taken.'.encode('utf-8'))
                return

        # create a list of user requests
        with open("user_credentials_requests.csv", 'r') as requests_file:
            requests_reader = csv.reader(requests_file)
            # create a list of all requests
            requests = list(requests_reader)

        # check if the username is already taken by requested user
        for request in requests:
            if request and request[0] == username:
                conn.sendall('Username is already taken.'.encode('utf-8'))
                return

        # add the new user to the list of requests
        hashed_password, salt = hash_and_salt(password)
        requested_credentials = [username, hashed_password, salt]

        # append the list of requests to user_credentials_requests.csv
        with open("user_credentials_requests.csv", 'a', newline='') as requests_file:
            requests_writer = csv.writer(requests_file)
            requests_writer.writerow(requested_credentials)

        conn.sendall('Request sent successfully!'.encode('utf-8'))
        conn.close()
        return
    except Exception as e:
        print(f"[!] Error: {e}")
        conn.sendall('Request failed.'.encode('utf-8'))
        conn.close()
        return


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

            received_operation = client_conn.recv(1024).decode()  # listen for an incoming message

            if received_operation == 'login':
                # Spawn a new thread for each client to handle authentication
                auth = Thread(target=authenticate_user, args=(client_conn, separator_token))
                auth.start()

                clients.add(client_conn)

                # start a new thread that listens for each client's messages
                listen_thread = Thread(target=listen_for_messages, args=(client_conn, client_addr, clients))
                listen_thread.start()
                continue
            elif received_operation == 'register':
                # start a new thread to handle user registration
                register_thread = Thread(target=register_user, args=(client_conn, separator_token))
                register_thread.start()

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
