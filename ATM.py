import random
import mysql.connector

# Connect to MySQL database
def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root")
    return connection

# Create the ATM database if it doesn't exist
def create_database(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS atm")

# Create the 'accounts' table if it doesn't exist
def create_table(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS accounts (
        account_number INT PRIMARY KEY,
        name VARCHAR(20),
        password VARCHAR(20),
        balance INT,
        quick_withdraw INT,
        is_locked BOOLEAN,
        login_attempts INT
    )""")

# Check if the 'accounts' table exists in the database
def table_exists(cursor):
    cursor.execute("SHOW TABLES LIKE 'accounts'")
    return cursor.fetchone() is not None

# Generate a random account number
def generate_account_number():
    return random.randint(1000000, 9999999)

# Create a new account
def create_account(connection, cursor):
    while True:
        account_number = generate_account_number()

        cursor.execute("SELECT * FROM accounts WHERE account_number = %s", (account_number,))
        account = cursor.fetchone()

        if not account:
            break

    name = input("Enter your name: ")
    password = input("Enter a password(Password should be very strong): ")
    balance = int(input("Enter the initial balance: "))
    quick_withdraw = int(input("Enter the quick withdraw limit: "))
    is_locked = False
    login_attempts = 0

    cursor.execute("""INSERT INTO accounts
        (account_number, name, password, balance, quick_withdraw, is_locked, login_attempts)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (account_number, name, password, balance, quick_withdraw, is_locked, login_attempts))
    connection.commit()
    print("Account created successfully. Account number:", account_number)

# Log in to an existing account
def login(connection, cursor):
    account_number = int(input("Enter your account number: "))
    password = input("Enter your password: ")

    cursor.execute("SELECT * FROM accounts WHERE account_number = %s", (account_number,))
    account = cursor.fetchone()

    if account and account[2] == password:
        print("Login successful. Welcome,", account[1])
        account = list(account)  # Convert the account tuple to a list
        logged_in = True
        while logged_in:
            logged_in = account_menu(connection, cursor, account)
    else:
        print("Invalid account number or password.")

# Display the account menu
def account_menu(connection, cursor, account):
    print("___________________________")
    print("         --- Account Menu ---           ")
    print("1. Show balance                           ")
    print("2. Deposit                                   ")
    print("3. Withdraw                                ")
    print("4. Change account details           ")
    print("5. Logout                                    ")
    print("___________________________")

    choice = input("Enter your choice: ")

    if choice == "1":
        show_balance(account)
    elif choice == "2":
        deposit(connection, cursor, account)
    elif choice == "3":
        withdraw(connection, cursor, account)
    elif choice == "4":
        change_account_details(connection, cursor, account)
    elif choice == "5":
        print("Logged out successfully.")
        return False
    else:
        print("Invalid choice. Please try again.")

    return True

# Show account balance
def show_balance(account):
    print("--- Account Balance ---")
    print("Balance:", account[3])

# Deposit funds into the account
def deposit(connection, cursor, account):
    amount = int(input("Enter the amount to deposit: "))
    new_balance = account[3] + amount

    cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s",
                   (new_balance, account[0]))
    connection.commit()
    print("Deposit successful. New balance:", new_balance)
    account[3] = new_balance  # Update the account balance in the account list

# Withdraw funds from the account
def withdraw(connection, cursor, account):
    print("_______________________")
    print("      --- Withdraw Menu ---    ")
    print("1. Regular Withdraw            "    )
    print("2. Quick Withdraw               "     )
    print("_______________________")
    choice = input("Enter your choice: ")

    if choice == "1":
        regular_withdraw(connection, cursor, account)
    elif choice == "2":
        quick_withdraw(connection, cursor, account)
    else:
        print("Invalid choice. Please try again.")

# Regular withdraw
def regular_withdraw(connection, cursor, account):
    amount = int(input("Enter the amount to withdraw: "))

    if amount <= account[3]:
        new_balance = account[3] - amount
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s",
                       (new_balance, account[0]))
        connection.commit()
        print("Regular withdraw successful. New balance:", new_balance)
        account[3] = new_balance  # Update the account balance in the account list
    else:
        print("Insufficient balance.")

# Quick withdraw
def quick_withdraw(connection, cursor, account):
    quick_limit = account[4]

    if quick_limit <= account[3]:
        new_balance = account[3] - quick_limit
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s",
                       (new_balance, account[0]))
        connection.commit()
        print("Quick withdraw of", quick_limit, "successful. New balance:", new_balance)
        account[3] = new_balance  # Update the account balance in the account list
    else:
        print("Insufficient balance for quick withdraw.")

# Change account details
def change_account_details(connection, cursor, account):
    print("--- Change Account Details ---")
    new_name = input("Enter a new name (leave blank to keep current name): ")
    new_password = input("Enter a new password (leave blank to keep current password): ")

    if new_name or new_password:
        update_values = {}
        if new_name:
            update_values["name"] = new_name
        if new_password:
            update_values["password"] = new_password

        update_query = "UPDATE accounts SET "
        update_query += ", ".join("{} = %s".format(key) for key in update_values.keys())
        update_query += " WHERE account_number = %s"

        cursor.execute(update_query, tuple(update_values.values()) + (account[0],))
        connection.commit()
        print("Account details updated.")
    else:
        print("No changes made to account details.")

# Show all accounts in the database
def show_accounts(cursor):
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()

    if not accounts:
        print("No accounts found.")
    else:
        print("--- Accounts ---")
        for account in accounts:
            print("Account Number:", account[0])
            print("Name:", account[1])
            print("---")

# Main program
def main():
    connection = connect_to_database()
    if connection is None:
        return

    cursor = connection.cursor()
    create_database(cursor)
    connection.database = "atm"
    create_table(cursor)

    while True:
        print("________________________")
        print("   --- ATM Management ---     ")
        print("1. Create account                 ")      
        print("2. Login                                ")
        print("3. Show accounts                 ")
        print("4. Exit                                   ")
        print("________________________")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_account(connection, cursor)
        elif choice == "2":
            login(connection, cursor)
        elif choice == "3":
            show_accounts(cursor)
        elif choice == "4":
            print("Exiting...")
            print("THANK YOU")
            break
        else:
            print("Invalid choice. Please try again.")

    cursor.close()
    connection.close()

# Start the program
if __name__ == "__main__":
    main()
