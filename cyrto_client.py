import socket
import pickle
import time

class Wallet:
    def __init__(self, name, initial_balance=0):
        self.name = name
        self.balance = initial_balance
        self.transactions = []

    def check_balance(self):
        return self.balance

    def add_transaction(self, recipient, amount, node_socket):
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

        # Wait for the response from the blockchain node
        response = pickle.loads(node_socket.recv(1024))

        if response.get("type") == "transaction_result":
            if response.get("success"):
                self.transactions.append(transaction)
                self.balance -= amount
                print("Transaction successful.")
            else:
                print("Transaction failed.")
        else:
            print("Invalid response from the blockchain node.")

def display_blockchain(node_socket):
    node_socket.sendall(pickle.dumps({"type": "get_blockchain"}))
    blockchain_data = pickle.loads(node_socket.recv(1024))
    if "chain" in blockchain_data:
        chain = blockchain_data["chain"]
        for block in chain:
            print(f"Block #{block['index']}")
            print(f"Hash: {block['hash']}")
            print(f"Previous Hash: {block['previous_hash']}")
            print(f"Timestamp: {block['timestamp']}")
            print(f"Data: {block['data']}")
            print(f"Nonce: {block['nonce']}")
            print("")

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
        print("3. Display Blockchain")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            balance = client_wallet.check_balance()
            print(f"{client_wallet.name}'s Wallet Balance: {balance}")
        elif choice == "2":
            recipient = input("Enter recipient's name: ")
            amount = float(input("Enter transaction amount: "))
            client_wallet.add_transaction(recipient, amount, node_socket)
        elif choice == "3":
            display_blockchain(node_socket)
        elif choice == "4":
            node_socket.close()
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
