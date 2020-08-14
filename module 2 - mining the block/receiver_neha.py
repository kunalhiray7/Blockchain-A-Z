# Module 1 - create a blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        next_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(next_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                next_proof = next_proof + 1
            
        return next_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
        
    def is_chai_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if(block['previous_hash'] != self.hash(prev_block)):
                return False
            proof = block['proof']
            prev_proof = prev_block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if(hash_operation[:4] != '0000'):
                return False
                
            prev_block = block
            block_index += 1
            
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender, 'receiver': receiver, 'amount': amount})
        prev_block = self.get_previous_block()
        return prev_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/chain')
            if(response.status_code == 200):
                json_response = response.json()
                length = json_response['length']
                chain = json_response['chain']
                if(length > max_length and self.is_chai_valid(chain)):
                    max_length = length
                    longest_chain = chain
        
        if(longest_chain):
            self.chain = longest_chain
            return True
        return False
            
        
app = Flask(__name__)

## Creating node address for port 5000
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_previous_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Neha', amount = 2)
    block = blockchain.create_block(proof, prev_hash)
    response = {'message': 'New block is mined!', 'block': block}
    return jsonify(response), 200
    
@app.route('/chain', methods=['GET'])
def get_chain():
    chain = blockchain.chain
    return jsonify({'chain': chain, 'length': len(chain)}), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    return jsonify({'is_valid': blockchain.is_chai_valid(blockchain)}), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transactions():
    request_body = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in request_body for key in transaction_keys):
        return 'Invalid request', 400
    index = blockchain.add_transaction(request_body['sender'], request_body['receiver'], request_body['amount'])
    response = {'message': f'The transaction will be added to block with index {index}'}
    return jsonify(response), 201

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json_request = request.get_json()
    nodes = json_request.get('nodes')
    if nodes is None:
        return 'No node to connect!', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Node are connected, total nodes are: ' + str(len(blockchain.nodes)),
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    response = None
    is_replaced = blockchain.replace_chain()
    if is_replaced:
        response = {'message': 'Chain is replaced',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Chain is as it was',
                    'new_chain': blockchain.chain}
    return jsonify(response), 200
    
# Running the app
app.run(host='0.0.0.0', port=5002)


                