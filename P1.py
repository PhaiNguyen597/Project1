from logging import RootLogger
from turtle import up
import mysql.connector
import p1_data as p
import p1_users
import p1_games
import time
import logging
from datetime import datetime

cnx = mysql.connector.connect(user="root", password=p.password, database="220711_w2")
cursor = cnx.cursor(buffered=True)

game_database = "games"
user_database = "users"
log_database = "log"
logging.basicConfig(filename="log.txt", level=logging.DEBUG)

print("*** WELCOME TO PHAI'S SOME-WHAT SECURE GAME STORE: ***")
print("To get started, type /help for a list of commands")
global running
running = True
global curruser
curruser = "Guest"
global user_lst
user_lst = []
global game_lst
game_lst = []
global role
role = 0
global user_obj
user_obj = p1_users.User(0, "Guest", "123", "Guest", "Guest", "Guest", 0)


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
            print("/games - Display all games you own")
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
            print("/changerole - Makes a specified user's role into another role")
            print("/logs - Checks the buying/selling logs")

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
    elif command == "/games":
        read_owned_data()
    elif command == "/sell":
        sell_game()
    elif command == "/discount":
        discount_game()
    elif command == "/displayusers":
        display_users()
    elif command == "/credit":
        credit_user()
    elif command == "/changerole":
        change_role()
    elif command == "/logs":
        logs()
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
    elif table == "owned":
        add_cmd = f"INSERT INTO owned (id, title) VALUES ('{data[0]}', '{data[1]}')"
        cursor.execute(add_cmd)
        cnx.commit()


# Deletes certain data in specified table
def delete_data(id, table):
    del_cmd = f"DELETE FROM {table} WHERE id = {id}"
    cursor.execute(del_cmd)
    cnx.commit()


# Update certain data in specified table
def update_data(id, data, table):
    if table == "games":
        update_cmd = f"UPDATE games SET price = {data[1]} WHERE id = '{id}'"
        cursor.execute(update_cmd)
        cnx.commit()
    elif table == "users" and type(data) == int:
        update_cmd = f"UPDATE users SET credit = {data} WHERE id = '{id}'"
        cursor.execute(update_cmd)
        cnx.commit()
    elif table == "users" and type(data) != int:
        update_cmd = f"UPDATE users SET role = '{data}' WHERE id = '{id}'"
        cursor.execute(update_cmd)
        cnx.commit()


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
    logging.info(
        f"{fname} {lname} registered under the username {username} on {datetime.now()}"
    )
    print("User registered sucessfully! Consult your admin to raise permission level")
    add_cmd = f"INSERT INTO {user_database} (username, password, Firstname, Lastname, role, credit) VALUES('{username}','{pw}','{fname}','{lname}','Customer', 60)"
    cursor.execute(add_cmd)
    cnx.commit()


# Logs the user in
def login_user():
    global user_lst
    global curruser
    global role
    global user_obj
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
    global role
    if check_login() == False:
        print("Not currently logged in!")
    else:
        curruser = "Guest"
        role = 0
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


def display_users():
    global user_lst
    global role
    if role < 3:
        print("Insufficient permissions!")
        return
    for elem in user_lst:
        print(
            f"ID: {elem.id}      Username: {elem.username}       First Name: {elem.fname}       Last Name: {elem.lname}       Role: {elem.role}       Credit: ${elem.credit}"
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
        last_game = 0
        first_game = 100000000000
        for elem in game_lst:
            if int(elem.id) > last_game:
                last_game = int(elem.id)
            if int(elem.id) < first_game:
                first_game = int(elem.id)
        chosen_game = int(
            input("Enter the number of the game you would like to buy: >>>")
        )
        if chosen_game > last_game or chosen_game < first_game:
            print("ERROR: Game id does not exist!\nReturning to main menu...")
        else:
            for elem in game_lst:
                if int(elem.id) == chosen_game:
                    game_obj = p1_games.Game(elem.id, elem.title, elem.price)
                    if user_obj.credit < game_obj.price:
                        print("Insufficient credits!")
                    else:
                        data_lst = []
                        data_lst.append(user_obj.id)
                        data_lst.append(game_obj.title)
                        print("Game bought sucessfully!")
                        delete_data(elem.id, "games")
                        add_data(data_lst, "owned")
                        logging.info(
                            f"{user_obj.username} bought {game_obj.title} for ${game_obj.price} on {datetime.now()}"
                        )
    except ValueError:
        print("Must be number!\nReturning to main menu...")


# Checks if username is taken for /register
def check_existing_user(username):
    global user_lst
    for data in user_lst:
        if data.username == username:
            return True
    return False


# Adds a game to the games database to sell.
def sell_game():
    global curruser
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
    print(f"Game put on the shelf sucessfully for ${price}")
    logging.info(
        f"{curruser} put the game {title} on the shelf for ${price} on {datetime.now()}"
    )
    add_data(data_lst, game_database)

#Applies a percentage discount to one of the games.
def discount_game():
    global user_obj
    global game_lst
    global role
    global curruser
    if role < 2:
        print("Insufficient permission.\nReturning to main menu...")
        return
    print("ALL GAMES: ")
    for elem in range(len(game_lst)):
        print(
            f"{game_lst[elem].id})Title: {game_lst[elem].title} Price: {game_lst[elem].price}"
        )
    try:
        last_game = 0
        first_game = 100000000000
        for elem in game_lst:
            if int(elem.id) > last_game:
                last_game = int(elem.id)
            if int(elem.id) < first_game:
                first_game = int(elem.id)
        chosen_game = int(
            input("Enter which game you would like to apply a discount to: >>>")
        )
        if chosen_game > last_game or chosen_game < first_game:
            print("Invalid selection!\nReturning to main menu...")
            return
        amount = float(
            input(
                "Enter the amount you would like to discount the chosen game by as a percentage (0-1): >>>"
            )
        )
        if amount > 1 or amount < 0:
            print("Invalid percentage!\nReturning to main menu...")
            return
        for elem in game_lst:
            if elem.id == chosen_game:
                price = elem.price
                title = elem.title
        new_price = format(price - (price * amount))
        data_lst = []
        data_lst.append(title)
        data_lst.append(new_price)
        update_data(chosen_game, data_lst, game_database)
        print(f"Sucessfully changed price of {title} to ${new_price}")
        logging.info(
            f"{curruser} applied a discount of ${price * amount} to {title}, bringing the total to ${new_price} on {datetime.now()}"
        )
    except:
        print("Invalid input.\nReturning to main menu...")

#Gives a specified user a specified amount of credits
def credit_user():
    global role
    global user_lst
    global curruser
    total = 0
    if role < 3:
        print("Insufficient permission")
        return

    display_users()
    try:
        id = int(
            input("Enter the number of the user you would like to give credit to: >>> ")
        )
        amount = int(input("Enter how much credits you would like to give them: "))
        for elem in user_lst:
            if elem.id == id:
                total += amount + elem.credit
                update_data(elem.id, total, "users")
                print(f"Sucessfully gave ${amount} to {elem.username}")
                logging.info(
                    f"{curruser} gave ${amount} to {elem.username} on {datetime.now()}"
                )
                return
        print(f"Couldn't find user with id {id}")
        return
    except:
        print("ERROR: INTEGER expected")

#Changes the role of a specified user to a specified role
def change_role():
    global role
    global curruser
    global user_lst
    if role < 3:
        print("Insufficient permissions!\nReturning to main menu...")
        return
    display_users()
    try:
        id = int(
            input("Enter the number of the user you would like to change role: >>>")
        )
        new_role = input(
            "Would you like to change their role to Customer, Assosciate, or Admin? "
        )
        if new_role == "Customer" or new_role == "Assosciate" or new_role == "Admin":
            for elem in user_lst:
                if elem.id == id:
                    update_data(elem.id, new_role, "users")
                    print(f"Changed {elem.username}'s role to {new_role}")
                    logging.info(
                        f"{curruser} changed {elem.username}'s role to {new_role} on {datetime.now()}"
                    )
                    return
        else:
            print("Incorrect value inputted.\nReturning to main menu...")
            return
        print(f"Couldn't find user with id {id}")
    except:
        print("ERROR: Incorrect input received.\nReturning to main menu...")

#Reads all games in stock to global list
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
        id = record[0]
        username = record[1]
        pw = record[2]
        fname = record[3]
        lname = record[4]
        role = record[5]
        credit = record[6]
        user = p1_users.User(id, username, pw, fname, lname, role, credit)
        user_lst.append(user)

#Reads data of owned games for SPECIFIC user
def read_owned_data():
    global curruser
    global user_lst
    if check_login() == False:
        print("Not logged in!")
        return
    for elem in user_lst:
        if elem.username == curruser:
            try:
                query = f"SELECT * FROM owned WHERE id = '{elem.id}'"
                cursor.execute(query)
                print("Games owned:")
                for record in cursor:
                    print(f"1) {record[1]}")
            except:
                print(
                    "No games owned! Try buying one with /buy\nReturning to main menu..."
                )

#Prints the entirety of logs.txt to console
def logs():
    global role
    if role < 3:
        print("Insufficient permissions!")
        return
    with open("log.txt", "r") as logs:
        for line in logs:
            print(line, end="")


main()

cnx.close()
cursor.close()
