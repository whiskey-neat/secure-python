import pandas as pd

users_df = pd.read_csv("./ApplicationFiles/Login/users.csv")
taken_usernames = []


def get_existing_usernames():
    for i in range(len(users_df)):
        taken_username = users_df.iloc[i, 0]   # extract taken usernames
        taken_usernames.append(taken_username)
    return taken_usernames


def validatedetails(username, password):
    # create a list for usernames and passwords
    users_passwds_list = []
    # extract usernames and passwords
    for i in range(len(users_df)):
        existing_username = users_df.iloc[i, 0]
        username_password = users_df.iloc[i, 1]
        # save existing username and password pair as a tuple
        userdetails = (existing_username, username_password)
        users_passwds_list.append(userdetails)
    
    # convert the list of tuples to a dictionary
    users_dict = dict(users_passwds_list)

    if username in users_dict:
        print("Checking password for username:", username)
        print(users_dict[username])
        if password == users_dict[username]:
            print("Login Successful!")
            input("Press enter: ")
        else:
            print("Invalid login details")
            input("Press enter to try again")
    else:
        print("Invalid login details")
        input("Press enter to continue")
    