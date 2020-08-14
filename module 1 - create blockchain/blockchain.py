# Module 1 - create a blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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
        
    def is_chai_valid(self):
        prev_block = self.chain[0]
        block_index = 1
        while block_index < len(self.chain):
            block = self.chain[block_index]
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
            
        
app = Flask(__name__)

blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_previous_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof, prev_hash)
    response = {'message': 'New block is mined!', 'block': block}
    return jsonify(response), 200
    
@app.route('/chain', methods=['GET'])
def get_chain():
    chain = blockchain.chain
    return jsonify({'chain': chain, 'length': len(chain)}), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    return jsonify({'is_valid': blockchain.is_chai_valid()}), 200


# Running the app
app.run(host='0.0.0.0', port=5000)


                