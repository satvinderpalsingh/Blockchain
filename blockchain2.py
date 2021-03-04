import datetime  # to add timestamps on every block in blockchain
import hashlib  # library that is ued to hash the block
import json  # to communicate in json data
# Flask to implement webservices jsonify to see the jsop message/response
# request help us to connect all the nodes of the blockchain together froming the p2p network
from flask import Flask, jsonify, request
# it will help us to verify that all the blockchain have same blockhain or not http requests (used in replace_cahin)
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Building a Blockchain


class Blockchain:

    def __init__(self):
        self.chain = []  # our main block chain
        # now we will create the list of transation which will record the all transactions
        self.transactions = []
        # create_block used to create the block in blockchain so it is executed only when the block is mined(meaning it has winnnig proof_of_work=proof)    proof=0 and previous_hash='0' for the genesis block
        self.create_block(proof=0, previous_hash='0')
        # nodes will contains the unique identifier of the address of all nodes in p2p network
        self.nodes = set()  # we have taken set() instead of list because we know that address are randomly generated by uuid4 to avoid duplicacy in it
    # part1

    def create_block(self, proof, previous_hash):
        block = {  # dictionary of python data structure
            'index': len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,  # works like a nounce of block stops when we reach at or below the target
            'previous_hash': previous_hash,
            'transactions': self.transactions}
        self.transactions = []  # this need to be done bcoz we cant have duplicates lists of transactions in the further blocks so empty the transation that had been added in the block
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof  # it is just a no. corresponding to the game solved by person is having a hash with trailing 4 zeroe's

    # hash of a block is created after generating block thats we have only use previous_hash because its already created
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        # reference of first block stored genesis block
        previous_block = chain[0]
        block_index = 1  # required for iteration
        while block_index < len(chain):
            block = chain[block_index]  # cuurent block
            # checking weather the refernce stored in property previus_hash is currently matched or not with the hash of previous block using hash function
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            # verfying the proof of block with the data proof and previous proof it is easy then creating the proof
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            # the more is zero's the more is harder to mine the block
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    # functions used to get add the transactions to the lists
    def add_transaction(self, senders, receiver, amount):
        self.transactions.append({
            'senders': senders,
            'receiver': receiver,
            'amount': amount
        })
        previous_block = self.get_previous_block()
        # +1 beacause before mining the transaction are added so new_block index will be +1 then previous
        return previous_block['index']+1
    # part-1 ends

    # part-3--> dealing with decentarlized application and transactions

    # this function allow us to add different nodes to chain

    def add_node(self, address):  # generating the decentarlized application
        # we need to parse the url before adding it
        parsed_url = urlparse(address)
        # .netloc gives us the unique identifier of the node address removing the unrequired part from it
        self.nodes.add(parsed_url.netloc)

    # this function help us to solve the problem of consensus protocols (competing chain)

    def replace_chain(self):
        # this variable help us to find the length of longest chain among different network
        max_length = len(self.chain)
        longest_chain = None
        network = self.nodes  # this variable will hold the address of all the nodes in network
        for node in network:
            # we know the nodes array will hold only the netlock value in nodes so we are going to use taht and make a request to that node check its length
            # using the requests library we make a requests to that node address ([f'http://{node}/get_chain']  -->  [f'http://127.0.0.5000/get_chain')]
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:  # this ids the vode chaeck something is received in request
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
            # this will happen in every node of network
        if longest_chain:
            # if this chain is shorter than otherit will be updated
            self.chain = longest_chain
            return True
            # if this chain is only longest in network than return false and no update
        return False
    # part-3 ends
# Mining our Blockchain


app = Flask(__name__)

# Creating a Blockchain
# creating the instance of blockchain
blockchain = Blockchain()

# Mining the blockchain
# create an random and unique address for the node on port 5000
# this is the address used by to send the whale coin when the miner mines the wahle coin
node_address = str(uuid4()).replace('-', '')

# part-2


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    # miners price
    # usually the reciever public address is created when  user generate the wallet and mining pool send the coin after mining the block to miner address present in the bat file which is edited after downloading the software
    blockchain.add_transaction(node_address, 'Prabjot', 1)
    # when created blockchain is called all the transactions performed will be inserted inside the current created block and when appended in transactions it will be again change to [] empty to avoid the duplicacy
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block! 😈😈😈😈😈🤓🤓🤓',  # response is a json data
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

# getting all blocks in chain


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

# custom message


@app.route('/', methods=['GET'])
def custom_message():
    response = {
        'message': 'Congratulations you are on Whalecoin 🐳🐳🐳🐳🐳🐳'
    }
    return jsonify(response), 200

# part-2 ends
# creating the transactions


@app.route('/add_transactions', methods=['POST'])
def add_transaction():
    # this will help us to extract te post request made in postman like req.params.name in express
    json = request.get_json()
    # this will hep us to check that all the parameters are present or not for adding the transactions
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(
        json['sender'], json['receiver'], json['amount'])
    # when the block is mined all the transations in lists is added to block
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()  # we will get request message send from postman
    # {'nodes':['http://127.0.0.1:5000','http://127.0.0.1:5001','http://127.0.0.1:5003',...]} when adding nodes using add_nodes 127.0.0.1:5001 it will be extracted using netloc
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)  # add our nodes to network
    response = {'message': 'All the nodes are now connected. The Whalecoin 🐳🐳🐳🐳🐳🐳 Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
# this function will present in every node of blockchain and always checked so that the node remain upadatesd with other blockchains by hitiing replace_chain URL


@ app.route('/replace_chain', methods=['GET'])
def replace_chain():
    # using the above defined function in class
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:  # means the current blockchain was the shortest one and it is replaced
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:  # means the current blockchain was not the shortest one and it is not replaced
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


# Running the app
# host= '0.0.0.0' specifies that it is available publicily
app.run(host='0.0.0.0', port=5002)
