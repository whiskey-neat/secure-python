import checkuser
import re


def password_strength_check(password):
    errors = 0
    error_message = ""

    while True:
        # is the password longer or equal to 8?
        if len(password) <= 8:
            errors = 1
            error_message = "Password must be 8 characters or longer"
            break
        # does the password contain a lowercase character?
        elif not re.search(r"[a-z]", password):
            errors = 1
            error_message = "Password must contain a lowercase character"
            break
        # does the password contain an uppercase character?
        elif not re.search(r"[A-Z]", password):
            errors = 1
            error_message = "Password must contain an uppercase character"
            break
        # does the password contain a number?
        elif not re.search(r"[0-9]", password):
            errors = 1
            error_message = "Password must contain a number"
            break
        # does the password contain a special character?
        elif not re.search(r"[ !\"#$%&'()*+,-./\\:;<=>?@[\]^_`{|}~]", password):
            errors = 1
            error_message = "Password must contain a special character"
            break
        # is the password "password"?
        elif re.search("\s", password):
            errors = 1
            error_message = "Password cannot contain whitespace characters"
            break
        else:
            errors = 0
            break

    return errors, error_message


def create_new_user():
    # user chooses username
    while True:
        new_username = input("Choose a username: ").lower()
        taken_usernames = checkuser.get_existing_usernames()
        if new_username in taken_usernames:
            print("Username is taken")
        else:
            break
    # user chooses password
    while True:
        new_passwd = input("Enter a password: ").strip()
        invalid_password, message = password_strength_check(new_passwd)
        if invalid_password:
            print(message)
        else:
            break

    user_login = new_username, ",", new_passwd, "\n"

    # save details to users file
    f = open("a./ApplicationFiles/Login/users.csv", 'a')
    f.write(''.join(user_login))
    f.close()

    print("Your account was created successfully! :)")
    input("Press any key to return to the login page: ")
    
