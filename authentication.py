import csv
import hashlib
import secrets


def hash_password(password, salt):
    salted_password = (password + salt).encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return hashed_password


def generate_salt():
    return secrets.token_hex(16)


def check_user_credentials(username, password):
    with open('user_credentials.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Username'] == username:
                stored_password = row['HashedPassword']
                salt = row['Salt']
                hashed_password = hash_password(password, salt)
                return hashed_password == stored_password
    return False


def write_to_csv(username, hashed_password, salt):
    with open('user_credentials.csv', 'a', newline='') as csvfile:
        fieldnames = ['Username', 'HashedPassword', 'Salt']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({'Username': username, 'HashedPassword': hashed_password, 'Salt': salt})
    print("User credentials have been stored in user_credentials.csv")


def get_user_credentials():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    return username, password


if __name__ == "__main__":
    username, password = get_user_credentials()
    salt = generate_salt()
    hashed_password = hash_password(password, salt)
    write_to_csv(username, hashed_password, salt)