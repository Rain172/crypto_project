import socket
import pickle
import threading
import time
import hashlib

DIFFICULTY = 4

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash
        self.nonce = nonce

    def calculate_hash(self):
        value = str(self.index) + str(self.previous_hash) + str(self.timestamp) + str(self.data) + str(self.nonce)
        return hashlib.sha256(value.encode()).hexdigest()

def proof_of_work(index, previous_hash, timestamp, data):
    nonce = 0
    target = "0" * DIFFICULTY
    while True:
        value = str(index) + str(previous_hash) + str(timestamp) + str(data) + str(nonce)
        hash = hashlib.sha256(value.encode()).hexdigest()
        if hash[:DIFFICULTY] == target:
            return nonce
        nonce += 1

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.lock = threading.Lock()  # Lock for thread safety

    def create_genesis_block(self):
        return Block(0, "0", int(time.time()), "Genesis Block", self.calculate_hash(0, "0", int(time.time()), "Genesis Block", 0), 0)

    def add_block(self, block):
        self.chain.append(block)

    def get_previous_block(self):
        return self.chain[-1]

    def create_new_block(self, nonce):
        previous_block = self.get_previous_block()
        index = previous_block.index + 1
        timestamp = int(time.time())
        transactions = list(self.pending_transactions)
        self.pending_transactions = []  # Clear pending transactions
        hash = self.calculate_hash(index, previous_block.hash, timestamp, transactions, nonce)
        return Block(index, previous_block.hash, timestamp, transactions, hash, nonce)

    def validate_blockchain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if (
                current_block.hash
                != self.calculate_hash(
                    current_block.index,
                    previous_block.hash,
                    current_block.timestamp,
                    current_block.data,
                    current_block.nonce,
                )
                or current_block.hash[:DIFFICULTY] != "0" * DIFFICULTY
            ):
                return False
        return True

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def calculate_hash(self, index, previous_hash, timestamp, data, nonce):
        value = str(index) + str(previous_hash) + str(timestamp) + str(data) + str(nonce)
        return hashlib.sha256(value.encode()).hexdigest()

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.peers = []
        self.blockchain = Blockchain()

    def listen_for_connections(self):
        self.socket.listen(5)
        print(f"Listening for connections on {self.host}:{self.port}")
        while True:
            client_socket, _ = self.socket.accept()
            peer = client_socket.getpeername()
            print(f"Accepted connection from {peer}")
            self.peers.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    message = pickle.loads(data)
                    if message.get("type") == "block":
                        self.handle_received_block(message["block"])
            except Exception as e:
                self.peers.remove(client_socket)
                print(f"Connection closed by peer {client_socket.getpeername()}, Error: {e}")
                break

    def handle_received_block(self, received_block):
        with self.blockchain.lock:  # Ensure thread safety
            if received_block.index > self.blockchain.get_previous_block().index:
                if self.blockchain.validate_blockchain():
                    self.blockchain.add_block(received_block)
                    self.broadcast_block(received_block)
                    print(f"Received and added new block #{received_block.index}")

    def broadcast_block(self, block):
        for peer_socket in self.peers:
            try:
                peer_socket.sendall(pickle.dumps({"type": "block", "block": block}))
            except Exception as e:
                self.peers.remove(peer_socket)
                print(f"Connection with peer {peer_socket.getpeername()} lost, Error: {e}")

def main():
    node1 = Node("10.0.97.119", 5000)  # Update with the appropriate IP address and port
    node2 = Node("10.0.97.119", 5001)  # Update with the appropriate IP address and port

    threading.Thread(target=node1.listen_for_connections).start()
    threading.Thread(target=node2.listen_for_connections).start()

    transaction1 = Transaction("Alice", "Bob", 10)
    node1.blockchain.add_transaction(transaction1)

    transaction2 = Transaction("Bob", "Charlie", 5)
    node2.blockchain.add_transaction(transaction2)

    new_block1 = node1.blockchain.create_new_block(proof_of_work(node1.blockchain.get_previous_block().index + 1, node1.blockchain.get_previous_block().hash, int(time.time()), node1.blockchain.pending_transactions))
    node1.blockchain.add_block(new_block1)
    node1.broadcast_block(new_block1)

    new_block2 = node2.blockchain.create_new_block(proof_of_work(node2.blockchain.get_previous_block().index + 1, node2.blockchain.get_previous_block().hash, int(time.time()), node2.blockchain.pending_transactions))
    node2.blockchain.add_block(new_block2)
    node2.broadcast_block(new_block2)

if __name__ == "__main__":
    main()
