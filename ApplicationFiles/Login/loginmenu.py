import os, datetime
import pyfiglet
import numpy as np
import pandas as pd
import existinguser
import createnewuser



def get_login_option(number):
    # # user chooses menu option
    option = input("\nSelect a option: ")

    # check the option is valid
    if option.isdigit() and 1 <= int(option) <= number:
        # input is valid and turn to integer
        return int(option)
    else:
        # input is invalid. Display an error message and continue the loop
        print("\nPlease enter a value between 1 and", number)

def loginmenu():
    ascii_banner = pyfiglet.figlet_format("python chat app")
    print(ascii_banner)

    print("You must be logged in to use this application:")
    print("\n1. Existing User\n2. New User\n3. Exit")
    while True:
            login_option = get_login_option(3)

            if login_option:
                break
        
    if login_option == 1:
        existinguser.existing_user_login()
    elif login_option == 2:
        createnewuser.create_new_user()
    else:
        quit()

while True:
    os.system("cls")
    loginmenu()