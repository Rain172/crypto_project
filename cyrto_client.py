import socket
import pickle
from time import sleep

def send_transaction(sender, recipient, amount, node_socket):
    transaction = {
        "sender": sender,
        "recipient": recipient,
        "amount": amount
    }
    message = {"type": "transaction", "transaction": transaction}
    node_socket.sendall(pickle.dumps(message))

def display_blockchain(node, node_name):
    print(f"Blockchain on {node_name} ({node.host}:{node.port}):")
    for block in node.blockchain.chain:
        print(f"Block #{block.index}")
        print(f"Hash: {block.hash}")
        print(f"Previous Hash: {block.previous_hash}")
        print(f"Timestamp: {block.timestamp}")
        print(f"Data: {block.data}")
        print(f"Nonce: {block.nonce}")
        print("")

def main():
    # Connect to nodes with the updated IP address
    node1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node1_socket.connect(("10.0.98.59", 4999))
    print("Connected to Node 1")

    node2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node2_socket.connect(("10.0.98.59", 5000))
    print("Connected to Node 2")

    # Send transactions to specific nodes
    send_transaction("Alice", "Bob", 10, node1_socket)
    send_transaction("Bob", "Charlie", 5, node2_socket)

    # Display blockchain status
    sleep(1)  # Give nodes time to process transactions and mine blocks
    node1_socket.sendall(pickle.dumps({"type": "get_blockchain"}))
    node2_socket.sendall(pickle.dumps({"type": "get_blockchain"}))

    # Receive and display blockchain
    node1_blockchain = pickle.loads(node1_socket.recv(1024))
    node2_blockchain = pickle.loads(node2_socket.recv(1024))
    display_blockchain(node1_blockchain, "Node 1")
    display_blockchain(node2_blockchain, "Node 2")

    node1_socket.close()
    node2_socket.close()

if __name__ == "__main__":
    main()
