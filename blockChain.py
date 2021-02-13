import datetime  # to add timestamps on every block in blockchain
import hashlib  # library that is ued to hash the block
import json  # to communicate in json data
# Flask to implement webservices jsonify to see the jsop message/response
from flask import Flask, jsonify


class Blockchain:

    def __init__(self):
        self.chain = []  # our main block chain
        # create_block used to create the block in blockchain so it is executed only when the block is mined(meaning it has winnnig proof_of_work=proof)    proof=0 and previous_hash='0' for the genesis block
        self.create_block(proof=0, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {  # dictionary of python data structure
            'index': len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    def get_previous_hash(self):
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

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0] # reference of first block stored genesis block
        block_index = 1 # required for iteration
        while block_index < len(chain): 
            block = chain[block_index] # cuurent block
            if block['previous_hash'] != self.hash(previous_block): # checking weather the refernce stored in property previus_hash is currently matched or not with the hash of previous block using hash function
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            # verfying the proof of block with the data proof and previous proof
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
