import sqlite3
import re
import random                                                                                
class Users:
    def __init__(self, user_id, username, pin,contact, email, account_number, balance):
        self._user_id = user_id
        self._username = username
        self._pin = pin
        self._contact = contact
        self._email = email
        self._account_number = account_number
        self._balance = balance

    def get_balance(self):
        return self._balance
    
    def set_balance(self,amount):
        self._balance = amount
    
    def display_balance(self):
        print(f"Your current balance is: ${self._balance}")

    def deposit(self, amount):
        self._balance += amount
        print(f"Deposit: +${amount}")

    
    def withdraw(self, amount):
        if amount <= self._balance:
            self._balance -= amount
            print(f"Withdrawal: -${amount}")
            return True
        else:
            print("Insufficient Funds!")
            return False
    
    def get_user_id(self):
        return self._user_id
    
    def get_username(self):
        return self._username

    def get_pin(self):
        return self._pin
    
    def get_contact(self):
        return self._contact
 
    def display_welcome(self):
        print(f"\nWelcome, Mr. {self._username}!")

class Atm:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_table()
        self.users = {}

    def create_table(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = self.cursor.fetchone()

        if not table_exists:
            self.cursor.execute("""
                CREATE TABLE users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    pin INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    balance INTEGER      
                )
            """)
            self.connection.commit()
            print("Table 'users' created successfully.")
        else:
            return


    def create_user(self, username, pin, email, contact, account_number):
        self.cursor.execute("""
                INSERT INTO users (username, pin, email, contact, account_number, balance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, pin, email, contact, account_number, 0.0))
        self.connection.commit()
        print("User created successfully!")

    def is_valid_username(self, username):                                                             
        return len(username) >=5 and re.match("^[a-z]+$", username)
    
    def is_valid_pin(self, pin):
        pin_str = str(pin)                                                                                       
        return len(pin_str) == 4 and pin_str.isdigit()
    
    def pin_matches_username(self, email, pin):                                              
        self.cursor.execute("SELECT * FROM users WHERE email = ? AND pin = ?", (email, pin))
        return (self.cursor.fetchone()) is not None

    def authenticate_user(self, email, pin):
        self.cursor.execute("SELECT * FROM users WHERE email = ? AND pin = ?", (email, pin))
        user_data = self.cursor.fetchone()
        if user_data:
            user_id, username, pin, email, contact, account_number, balance = user_data
            return Users(user_id, username, pin, contact, email, account_number, balance)
        else:
            print("Authentication failed! Incorrect Username or PIN.")
            return None
        
    def valid_email(self,email):                                                                               
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)
    
    def email_exists(self, email):                                                            
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return bool(self.cursor.fetchone())
    
    def account_exist(self, account_number):
        self.cursor.execute("SELECT * FROM users WHERE account_number = ?", (account_number,))
        return bool(self.cursor.fetchone())

    
    def valid_contact(self,contact):
        contact_re = r"^03\d{9}$"                                                                               
        return re.match(contact_re,contact)

    def update_balance(self, user):
        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (user.get_balance(), user.get_user_id()))
        self.connection.commit()
        user.display_balance()                                                                       

    def delete_account(self,email,pin):
        self.cursor.execute("DELETE FROM users WHERE email = ? AND pin = ?", (email,pin))
        self.connection.commit()

    def transfer_funds(self, user, amount, recipient_account=None):
        if amount > user.get_balance():
            print("Insufficent Balance for Transfer!")
            return
        self.cursor.execute("SELECT user_id, balance FROM users WHERE account_number = ?", (recipient_account,))
        recipient = self.cursor.fetchone()
        if recipient:
            recipient_id, recipient_balance = recipient
            user.set_balance(user.get_balance() - amount)
            recipient_balance += amount
            self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (user.get_balance(), user.get_user_id()))
            self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (recipient_balance, recipient_id))
            self.connection.commit()
            print(f"Transferred ${amount} to {recipient_account}.")
        else:
            print("Recepient Account does not Exist")
    

    def update_username(self, new_username, user_id):
        self.cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (new_username, user_id))
        self.connection.commit()

    def update_pin(self, new_pin, user_id):
        self.cursor.execute("UPDATE users SET pin = ? WHERE user_id = ?", (new_pin, user_id))
        self.connection.commit()

    def update_contact(self, new_contact, user_id):
        self.cursor.execute("UPDATE users SET contact = ? WHERE user_id = ?", (new_contact, user_id))
        self.connection.commit()

    def random_account_generator(self, username, email, contact):
        first_two_digits = str(random.randint(11,99))
        last_two_digits = str(random.randint(11,99))

        username_part = username[:2].upper()
        contact_part = contact[:2]
        email_part = email[:2].upper()

        account_number = first_two_digits + username_part + contact_part + email_part + last_two_digits
        return account_number

    def signup(self):
        while True:                                                                          
            username = input("Enter a Username: ")
            if not self.is_valid_username(username):
                print("Invalid username! It must be at least 5 characters long, with no numbers, capital letters, or special characters.")
            else:
                break
        while True:                                                                                   
            pin = input("Enter a PIN: ")
            if not self.is_valid_pin(pin):
                print("PIN Must be 4 Numerical Digits!")
            else:
                break
        while True:                                                                                         
            email = input("Enter Email: ")
            if not self.valid_email(email):
                print("Invalid Email!")
            elif self.email_exists(email):
                print("Email is already in use.")
            else:
                break
        while True:                                                                               
            contact = input("Enter a Contact Number: ")
            if not self.valid_contact(contact):
                print("Contact Must be 11 Numerical Digits and Start with 03!")
            else:
                break
        account_number = self.random_account_generator(username, email, contact)
        self.create_user(username, pin, email, contact, account_number)

def main():
    atm = Atm("atm.db")
    while True:
        print("\nWelcome to the ATM Machine.")
        print("1. Login\n2. Exit")
        choice = input("\nChoose 1 or 2: ")
        
        if choice == '1':
            email = input("\nEnter email: ")
            if not atm.email_exists(email):                                
                print("\nEmail Not Registered!")                                     
                print("\n1. Create New User\n2. Back")
                sub_choice = input("Enter Your Choice 1 or 2: ")
                if sub_choice == '1':
                    atm.signup() 
                    continue
                elif sub_choice == '2':
                    continue
                else:
                    print("Invalid Choice.")
                return
            pin= input("Enter PIN: ")
            if atm.is_valid_pin(pin):                                                 
                if atm.pin_matches_username(email, int(pin)):
                    user = atm.authenticate_user(email, int(pin))
                    if user:
                        user.display_welcome()
                        print("You are Logged in.")
                        while True:
                            print("\nChoose an Option:")
                            print("1. Cash Withdrawal       5. Account Information\n2. Balance Inquiries     6. User Update\n3. Deposit               7. Delete User\n4. Funds Transfer        8. Quit\n")
                            user_choice = input("\nEnter your Choice (1-8): ")
                            
                            if user_choice == '1':
                                
                                print("1. 1,000          5. 5,000\n2. 2,000          6. 10,000\n3. 3,000          7. Other Amount\n4. 4,000          8. Quit ")
                                withdraw_choice_1 = input("\nEnter Your Choice (1-8): ")
                                
                                if withdraw_choice_1 == '1':
                                    amount = 1000
                                elif withdraw_choice_1 == '2':
                                    amount = 2000
                                elif withdraw_choice_1 == '3':
                                    amount = 3000
                                elif withdraw_choice_1 == '4':
                                    amount = 4000
                                elif withdraw_choice_1 == '5':
                                    amount = 5000
                                elif withdraw_choice_1 == '6':
                                    amount = 10000
                                elif withdraw_choice_1 == '7':
                                    amount = float(input("\nEnter Withdrawal Amount: $"))
                                    if amount > 50000:
                                        print("Limit is Exceeded! Please enter amount below 50000.")
                                        continue
                                    elif amount < 500:
                                        print("Enter an Amount of Minimum 1000.")
                                        continue
                                elif withdraw_choice_1 == '8':
                                    continue
                                else:
                                    print("Invalid Choice.")
                                    continue

                                if user.withdraw(amount):
                                    atm.update_balance(user)
                                else:
                                    print("\nWithdrawal Failed.")

                            elif user_choice == '2':
                                user.display_balance()
                                
                            elif user_choice == '3':
                                print("\nDeposit into your Account\n1. Proceed\n2. Quit")
                                deposit_choice = input("Choose 1 or 2: ")
                                if deposit_choice == '1':
                                    while True:
                                        amount = float(input("\nEnter amount to deposit: $"))
                                        if amount <= 0:
                                            print("\nPlease Enter a Positive Amount.")
                                        elif amount % 100 !=0 :
                                            print("\nEnter in Mulitples of 100")
                                        else:
                                            user.deposit(amount)
                                            atm.update_balance(user)
                                            break
                                elif deposit_choice == '2':
                                    continue
                                else:
                                    print("Invalid Choice")
                            
                            elif user_choice == '4':
                                print("\nFunds Transfer\n1. Proceed\n2. Quit")
                                withdraw_choice = input("Choose 1 or 2: ")
                                if withdraw_choice == '1':
                                    recepient_account = input("\nEnter Recepient Account No: ")
                                    if not atm.account_exist(recepient_account):
                                        print("Account Does Not Exist")
                                        continue
                                    amount = float(input("Enter Amount: $"))
                                    atm.transfer_funds(user, amount, recepient_account)
                                    atm.cursor.execute("SELECT * FROM users WHERE email = ?", (recepient_account,))
                                elif withdraw_choice == '2':
                                    continue
                                else:
                                    print("Invalid Choice.")
   
                            elif user_choice == '5':
                                print(f"\nUsername = {user._username}")
                                print(f"Email    = {user._email} ")
                                print(f"Account No = {user._account_number}")
                                print(f"Contact  = {user._contact}")
                            elif user_choice == '6':
                                while True:
                                    print("\n1. Update Username\n2. Update PIN\n3. Update Contact\n4. Quit")
                                    update_choice_2 = input("\nEnter Your Choice (1-4): ")
                                    if update_choice_2 == '1':
                                        new_username = input("Enter New Username: ")
                                        if user._username == new_username:
                                            print("It is already in use.")
                                        else:
                                            if atm.is_valid_username(new_username):
                                                confirm_new_username = input("Confirm Username: ")
                                                if confirm_new_username == new_username:
                                                    atm.update_username(new_username, user.get_user_id())
                                                    print("\nUsername has been Updated!")
                                                else:
                                                    print("Username does not Match.")
                                            else:
                                                print("Invalid Username.")
                                    
                                    elif update_choice_2 == '2':
                                        new_pin = int(input("Enter new PIN: "))
                                        if user._pin == new_pin:
                                            print("PIN is already in use.")
                                        else:
                                            if atm.is_valid_pin(new_pin):
                                                confirm_new_pin = int(input("Confirm PIN: "))
                                                if confirm_new_pin == new_pin:
                                                    atm.update_pin(new_pin, user.get_user_id())
                                                    print("PIN has been Updated!")
                                                else:
                                                    print("PIN does not Match.")
                                            else:
                                                print("Invalid PIN.")

                                    elif update_choice_2 == '3':
                                        new_contact = input("Enter new Contact: ")
                                        if user.get_contact() == new_contact:
                                            print("Contact is already in use.")
                                        else:
                                            if atm.valid_contact(new_contact):
                                                confirm_new_contact = input("Confirm Contact: ")
                                                if confirm_new_contact == new_contact:
                                                    atm.update_contact(new_contact, user.get_user_id())
                                                    print("Contact has been Updated!")
                                                else:
                                                    print("Contact does not match.")
                                            else:
                                                print("Invalid Contact")
                                    
                                    elif update_choice_2 == '4':
                                        break
                                    else:
                                        print("Invalid Choice! Please choose a number between 1 and 4. ")

                            elif user_choice == '7':
                                print("\nDelete Account\n1. Proceed\n2. Quit")
                                delete_choice_1 = input("\nChoose 1 or 2: ")
                                if delete_choice_1 == '1':
                                    while True:
                                        delete_choice_2 = input("\nAre you sure you want to delete your account? (yes/no): ")
                                        if delete_choice_2 == 'yes':
                                            atm.delete_account(email,pin)
                                            print("Your Account has been Deleted")
                                            return
                                        elif delete_choice_2 == 'no':
                                            break
                                        else:
                                            print("\nInvalid Choice! Please Enter Yes or No.")
                                else:
                                    continue

                            elif user_choice == '8':
                                print("\nThank you for using the ATM!")
                                break

                            else:
                                print("Invalid choice. Please choose a number between 1 and .")
                    else:
                        print("Incorrect Username or PIN!")
                else:
                    print("Incorrect Username or PIN!")
            else:
                print("Incorrect Username or PIN!.")

        elif choice == '2':
            return None     
        
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
