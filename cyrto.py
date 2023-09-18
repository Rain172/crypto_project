import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce=0, hash=None):
        self.index = index  # Block's position in the chain
        self.previous_hash = previous_hash  # Hash of the previous block
        self.timestamp = timestamp  # Timestamp of when the block was created
        self.data = data  # Data stored in the block
        self.nonce = nonce  # Nonce used for Proof of Work
        self.hash = self.calculate_hash() if hash is None else hash  # Block's hash

    def calculate_hash(self):
        # Calculate the hash of the block based on its attributes
        value = str(self.index) + self.previous_hash + str(self.timestamp) + str(self.data) + str(self.nonce)
        return hashlib.sha256(value.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        # Initialize the blockchain with a list containing the genesis block
        self.chain = self.load_chain_from_file() or [self.create_genesis_block()]
        self.pending_transactions = []  # Transactions waiting to be mined
        self.wallets = self.load_wallets_from_file() or {"Wallet1": 100, "Wallet2": 100, "Wallet3": 100, "Wallet4": 100} # Loads the wallet from a file if there isn't one starts with defualt
        self.mining_reward = 10  # Reward for mining a block
        self.difficulty = 4  # Difficulty of PoW

    def save_chain_to_file(self):
        # Save the blockchain to a JSON file
        with open('blockchain.json', 'w') as file:
            json.dump([block.__dict__ for block in self.chain], file)

    def load_chain_from_file(self):
        # Load the blockchain from a JSON file, if it exists
        try:
            with open('blockchain.json', 'r') as file:
                data = json.load(file)
                return [Block(**block) for block in data]
        except FileNotFoundError:
            return None

    def save_wallets_to_file(self):
        # Save wallet balances to a JSON file
        with open('wallets.json', 'w') as file:
            json.dump(self.wallets, file)

    def load_wallets_from_file(self):
        # Load wallet balances from a JSON file, if it exists
        try:
            with open('wallets.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return None

    def create_genesis_block(self):
        # Create the first block (genesis block) of the blockchain
        return Block(0, "0", int(time.time()), "Genesis Block")

    def get_last_block(self):
        # Get the last block in the blockchain
        return self.chain[-1]

    def add_block(self, new_block):
        # Add a new block to the blockchain if it's valid
        if self.is_valid_block(new_block):
            self.chain.append(new_block)
            print("Block #{} has been added to the blockchain!".format(new_block.index))
            return True
        return False

    def is_valid_block(self, block):
        # Check the validity of a block
        if block.index != len(self.chain):
            return False
        if block.previous_hash != self.get_last_block().hash:
            return False
        if not self.is_valid_proof(block):
            return False
        return True

    def is_valid_proof(self, block):
        # Check if the Proof of Work for a block is valid
        guess = str(block.index) + block.previous_hash + str(block.timestamp) + str(block.data) + str(block.nonce)
        guess_hash = hashlib.sha256(guess.encode()).hexdigest()
        return guess_hash[:self.difficulty] == "0" * self.difficulty

    def mine_block(self, miner_address):
        # Mine a new block and add it to the blockchain
        reward = self.mining_reward  # Reward for mining a block
        transactions = self.pending_transactions[:]
        transactions.append({"from": "Network", "to": miner_address, "amount": reward})

        new_block = Block(len(self.chain), self.get_last_block().hash, int(time.time()), transactions)
        while not self.is_valid_proof(new_block):
            new_block.nonce += 1

        self.add_block(new_block)
        self.pending_transactions = []

        # Gives mining reward to miner's wallet
        self.wallets[miner_address] += reward

    def create_transaction(self, sender, recipient, amount):
        # Create a new transaction and update wallet balances
        if sender not in self.wallets or recipient not in self.wallets:
            print("Invalid sender or recipient.")
            return

        if self.wallets[sender] < amount:
            print("Insufficient balance in sender's wallet.")
            return

        transaction = {"from": sender, "to": recipient, "amount": amount}
        self.pending_transactions.append(transaction)
        self.wallets[sender] -= amount
        self.wallets[recipient] += amount
        print("Transaction created.")

# Initialize the blockchain
blockchain = Blockchain()

while True:
    print("\nOptions:")
    print("1: View Blockchain")
    print("2: Create Transaction")
    print("3: Mine Block")
    print("4: View Wallet Balances")
    print("5: Save Blockchain and Wallets")
    print("6: Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        # View the blockchain
        for block in blockchain.chain:
            print("\nBlock #{}".format(block.index))
            print("Timestamp: {}".format(block.timestamp))
            print("Data: {}".format(block.data))
            print("Hash: {}".format(block.hash))
    elif choice == "2":
        # Create a transaction
        sender = input("Enter sender's address: ")
        recipient = input("Enter recipient's address: ")
        amount = int(input("Enter amount to send: "))
        blockchain.create_transaction(sender, recipient, amount)
    elif choice == "3":
        # Mine a block
        miner_address = input("Enter miner's address: ")
        blockchain.mine_block(miner_address)
    elif choice == "4":
        # View wallet balances
        for wallet, balance in blockchain.wallets.items():
            print(f"{wallet}: {balance}")
    elif choice == "5":
        # Save the blockchain and wallets to files
        blockchain.save_chain_to_file()
        blockchain.save_wallets_to_file()
        print("Blockchain and Wallets saved.")
    elif choice == "6":
        # Exit the program
        break
    else:
        print("Invalid choice. Please try again.")