# file for existing user to login

import os, pyfiglet
import checkuser

def existing_user_login():
    os.system("cls")
    print(pyfiglet.figlet_format("Welcome Back!"))

    entered_username = input("Enter your username:")
    entered_passwd = input("Enter your password: ")

    # get a list of existing usernames
    existing_usernames = checkuser.get_existing_usernames()

    if entered_username in existing_usernames:
        checkuser.validatedetails(entered_username, entered_passwd)
        input("Press any key to go to login screen: ")
