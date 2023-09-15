import socket
import pickle

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
        print("3. Exit")
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
            node_socket.close()
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()