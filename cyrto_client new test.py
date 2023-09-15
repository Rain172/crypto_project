import socket
import pickle
import hashlib

class Wallet:
    def __init__(self, name, initial_balance=0):
        self.name = name
        self.balance = initial_balance
        self.transactions = []

    def check_balance(self):
        return self.balance

    def send_transaction(self, recipient, amount, node_socket):
        if amount <= 0:
            print("Invalid transaction amount.")
            return

        if self.balance < amount:
            print("Insufficient funds for the transaction.")
            return

        transaction = {
            "sender": self.name,
            "recipient": recipient,
            "amount": amount
        }
        message = {"type": "transaction", "transaction": transaction}
        node_socket.sendall(pickle.dumps(message))
        self.transactions.append(transaction)
        self.balance -= amount

def create_account(username, password):
    if username in users:
        print("Username already exists.")
    else:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        users[username] = hashed_password
        print("Account created successfully.")

def login(username, password):
    if username in users and users[username] == hashlib.sha256(password.encode()).hexdigest():
        print("Login successful.")
        return username  # Return the username on successful login
    else:
        print("Invalid username or password.")
        return None

def send_message(sender, recipient, content):
    if recipient in users:
        messages.append({'sender': sender, 'recipient': recipient, 'content': content})
        print("Message sent successfully.")
    else:
        print("Recipient does not exist.")

def check_messages(username):
    print(f"Messages for {username}:")
    for message in messages:
        if message['recipient'] == username:
            print(f"From: {message['sender']}")
            print(f"Message: {message['content']}")
            print("-" * 20)

def main():
    node_host = "10.0.97.119"  # Update with the appropriate IP address of the blockchain node
    node_port = 5000  # Update with the appropriate port of the blockchain node
    client_name = input("Enter your name: ")

    # Initialize the wallet with an initial balance (optional)
    client_wallet = Wallet(client_name, initial_balance=1000)

    node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   
    try:
        node_socket.connect((node_host, node_port))
    except Exception as e:
        print(f"Connection to the node at {node_host}:{node_port} failed. Error: {e}")
        return

    while True:
        print("\nOptions:")
        print("1. Check Wallet Balance")
        print("2. Send Transaction")
        print("3. Create an account")
        print("4. Log in")
        print("5. Send a message")
        print("6. Check messages")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            balance = client_wallet.check_balance()
            print(f"{client_wallet.name}'s Wallet Balance: {balance}")
        elif choice == "2":
            recipient = input("Enter recipient's name: ")
            amount = float(input("Enter transaction amount: "))
            client_wallet.send_transaction(recipient, amount, node_socket)
            print(f"Transaction sent: {amount} to {recipient}")
        elif choice == "3":
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            create_account(username, password)
        elif choice == "4":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            current_user = login(username, password)
        elif choice == "5":
            if 'current_user' in locals():
                recipient = input("Enter recipient's username: ")
                content = input("Enter your message: ")
                send_message(current_user, recipient, content)
            else:
                print("Please log in first.")
        elif choice == "6":
            if 'current_user' in locals():
                check_messages(current_user)
            else:
                print("Please log in first.")
        elif choice == "7":
            node_socket.close()
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
