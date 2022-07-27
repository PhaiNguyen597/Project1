from logging import RootLogger
import mysql.connector
import p1_data as p
import p1_users
import p1_games
import time

cnx = mysql.connector.connect(user="root", password=p.password, database="220711_w2")
cursor = cnx.cursor()

game_database = "games"
user_database = "users"
log_database = "log"


print("*** WELCOME TO PHAI'S SOME-WHAT SECURE GAME STORE: ***")
print("To get started, type /help for a list of commands")
global running
running = True
global curruser
curruser = "Yeti"
global user_lst
user_lst = []
global game_lst
game_lst = []
global role
role = 3
global user_obj
user_obj = p1_users.User("Guest", "123", "Guest", "Guest", "Guest", 0)


def main():
    global running
    global curruser
    global role
    while running:
        read_user_data()
        read_game_data()
        time.sleep(0.5)
        command = input(f"What would you like to do, {curruser}? >>>")
        run_command(command, role)


# Command to check for validity of commands
def run_command(command, role):
    global running
    if command == "/help":
        print("/help - Displays a list of commands")
        print("/login - Logs the user in")
        print("/register - Registers a user with a username and password")
        print("/exit - Exits out of the program.")
        # Customer commands
        if role >= 1:
            print("/logout - Logs the user out")
            print("/info - Displays info on your user only")
            print("/buy - Buys a specified game")
        # Assosciate commands
        if role >= 2:
            print("*** ASSOSCIATE COMMANDS ***")
            print("/sell - Adds a game for specified price into the stock")
            print(
                "/discount - Places a discount on an already existing game by percentages"
            )
        # Admin commands
        if role >= 3:
            print("*** ADMIN COMMANDS ***")
            print("/displayusers - Displays information of all the users")
            print("/credit - Give specified user amount of credit")
            print("/changeroll - Makes a specified user's role into another role")
            print("/logs - Checks the buying/selling logs")
            print("/removegame - Removes a game from stock")
            print("/removeuser - Removes a user from the database")
    elif command == "/login":
        login_user()
    elif command == "/logout":
        logout()
    elif command == "/info":
        display_user_info()
    elif command == "/register":
        register_user()
    elif command == "/buy":
        buy_game()
    elif command == "/sell":
        sell_game()
    elif command == "/exit":
        print("Now terminating program")
        time.sleep(1)
        running = False

    else:
        print("Invalid command. Type /help for a list of commands.")


# Adds certain data in specified table
def add_data(data, table):
    if table == user_database:
        add_cmd = f"INSERT INTO {user_database} (Firstname, Lastname, role) VALUES ('{data[0]}', '{data[1]}', '{data[2]}')"
        cursor.execute(add_cmd)
        cnx.commit()
    elif table == game_database:
        add_cmd = f"INSERT INTO {game_database} (title, price) VALUES ('{data[0]}', '{data[1]}')"
        cursor.execute(add_cmd)
        cnx.commit()


# Deletes certain data in specified table
def delete_data(id, table):
    del_cmd = f"DELETE FROM {table} WHERE id = {id}"
    cursor.execute(del_cmd)
    cnx.commit()


# Update certain data in specified table
def update_data(id, data, table):
    pass


# Registers a user to a unique username
def register_user():
    global user_lst
    username_loop = True
    fname = input("Enter your first name: >>>")
    lname = input("Enter your last name: >>>")
    while username_loop == True:
        username = input("Enter your desired username: >>>")
        if check_existing_user(username):
            print("That username already exists! Try another!")
        else:
            username_loop = False
    pw = input("Enter your desired password: >>>")

    user = p1_users.User(username, pw, fname, lname, "Customer", 60)
    user_lst.append(user)

    add_cmd = f"INSERT INTO {user_database} (username, password, Firstname, Lastname, role, credit) VALUES('{username}','{pw}','{fname}','{lname}','Customer', 60)"
    cursor.execute(add_cmd)
    cnx.commit()


# Logs the user in
def login_user():
    global user_lst
    global curruser
    global role
    global user_obj
    read_user_data()
    username = input("Enter in your username: >>>")
    password = input("Enter in your password: >>>")
    for elem in user_lst:
        if username == elem.username:
            if password == elem.pw:
                curruser = username
                user_obj = elem
                print("Log in successful!")
                if elem.role == "Customer":
                    role = 1
                elif elem.role == "Assosciate":
                    role = 2
                elif elem.role == "Admin":
                    role = 3
                else:
                    role = 0
                return
    print("Log in unsucessful. Please check your username/password")


# Checks if there's a user logged in
def check_login():
    global curruser
    if curruser == "Guest":
        return False
    return True


# Logs the user out
def logout():
    global curruser
    if check_login() == False:
        print("Not currently logged in!")
    else:
        curruser = "Guest"
        print("Logout successful!")


# Displays information on currently logged in user
def display_user_info():
    global curruser
    global user_lst
    global user_obj
    password_string = ""
    if check_login() == False:
        print("User is not logged in!")
    else:
        for i in range(len(user_obj.pw)):
            password_string += "*"
        print(
            f"Username: {user_obj.username}\nPassword: {password_string}\nFirst Name: {user_obj.fname}\nLast Name: {user_obj.lname}\nRole: {user_obj.role}\nCredit: ${user_obj.credit} "
        )


# Displays the entire table of games being sold and prompts user to choose which game they want to buy.
def buy_game():
    global user_obj
    global game_lst
    global role
    if role < 1:
        print("Insufficient permission.\nReturning to main menu...")
        return
    print("ALL GAMES: ")
    for elem in range(len(game_lst)):
        print(
            f"{game_lst[elem].id})Title: {game_lst[elem].title} Price: {game_lst[elem].price}"
        )
    try:
        chosen_game = int(
            input("Enter the number of the game you would like to buy: >>>")
        )
        if chosen_game > len(game_lst):
            print("ERROR: Game id does not exist!\nReturning to main menu...")
        else:
            for elem in game_lst:
                if int(elem.id) == chosen_game:
                    game_obj = p1_games.Game(elem.id, elem.title, elem.price)
                    if user_obj.credit < game_obj.price:
                        print("Insufficient credit!")
                    else:
                        print("Game bought sucessfully!")
    except ValueError:
        print("Must be number!\nReturning to main menu...")


# Checks if username is taken for /register
def check_existing_user(username):
    global user_lst
    read_user_data()
    for data in user_lst:
        if data.username == username:
            return True
    return False


# Adds a game to the games database to sell.
def sell_game():
    global role
    if role < 2:
        print("Insufficient permissions!\nReturning to main menu...")
        return
    title = input("Enter in the title of the game: >>>")
    try:
        price = float(input("Enter in the price: >>>"))
    except:
        print("Price must be a number!\nReturning to main menu...")
        return
    data_lst = []
    data_lst.append(title)
    data_lst.append(price)
    add_data(data_lst, game_database)


def read_game_data():
    global game_lst
    game_lst = []
    query = "SELECT * FROM games"
    cursor.execute(query)
    for record in cursor:
        id = str(record[0])
        title = record[1]
        price = record[2]
        game = p1_games.Game(id, title, price)
        game_lst.append(game)


# Reads data into a global list
def read_user_data():
    global user_lst
    user_lst = []
    query = "SELECT * FROM users"
    cursor.execute(query)
    for record in cursor:
        username = record[1]
        pw = record[2]
        fname = record[3]
        lname = record[4]
        role = record[5]
        credit = record[6]
        user = p1_users.User(username, pw, fname, lname, role, credit)
        user_lst.append(user)


main()

cnx.close()
cursor.close()
