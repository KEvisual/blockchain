from flask import Flask
import requests
from time import time
import hashlib
import json
import sys

chain = []
transactions = []
nodes = []
balance = 120
reward = 22
difficulty = 4
myWallet = "Karol Efrido"

def createHash(content):
    content_encoded = json.dumps(content, sort_keys=True).encode()
    return hashlib.sha256(content_encoded).hexdigest()

def createBlock(transactions, nonce, prevHash):
    index = len(chain)
    timestamp = time()
    content_block = f'{index}{timestamp}{transactions}{nonce}{prevHash}'
    hash = createHash(content_block)
    
    block = {
        'index': index,
        'timestamp': timestamp,
        'transactions': transactions,
        'nonce': nonce,
        'hash' : hash,
        'mined' : False
    }
    
    return hash, chain.append(block)

def getlastBlock():
    return chain[-1]

def proof_of_work(difficulty, index, hash_prev_block, transactions):
    hash_key = ""
    nonce = 0
    while(hash_key[:difficulty] != difficulty*"0"):
        nonce += 1
        hash_key = createHash(f'{index}{hash_prev_block}{transactions}{nonce}')
    return nonce, hash_key

def updateBlock(nonce, hash, mined):
    getlastBlock()["nonce"] = nonce
    getlastBlock()["hash"] = hash
    getlastBlock()["mined"] = mined
    
def update_blockchain():
    global chain, nodes
    new_chain = None
    max_length = len(chain)
    
    for node in nodes:   
        response = requests.get(f'https://{node}/blockchain')
        if response.status_code == 200:
            length = response.json()["length"]
            chain_node = response.json()["chain"]
            
            if length > max_length:
                max_length = length
                new_chain = chain_node
            
            if new_chain:
                chain = new_chain
                return True
            else:
                return False
            
# Create Genesis Block (1st Block)
createBlock([], 0, 64*"0")

app = Flask(__name__)
@app.route('/blockchain', methods = ["GET"])
def full_chain():
    response = {
        'chain': chain,
        'length': len(chain)
    }
    return json.dumps(response), 200

@app.route('/mine', methods = ["GET"])
def mine_block():
    global transactions, balance
    miner_reward = {
        "sender" : None,
        "recipient" : myWallet,
        "amount" : reward
    }
    
    transactions.append(miner_reward)
    total_transactions = len(getlastBlock()['transactions'])
    nonce, hash = proof_of_work(difficulty, len(chain), getlastBlock()["hash"], transactions)
    updateBlock(nonce, hash, True)
    prev_len_chain = len(chain)
    
    for miner in getlastBlock()['transactions']:
        if miner["sender"] == None:
            balance += miner["amount"]
    
    createBlock(transactions, 0, getlastBlock()["hash"])
    
    if len(chain) == prev_len_chain+1:
        transactions = []
        response = {
            'Messange' : 'New Block Mined!!!',
            'Nonce': nonce,
            'Hash' : hash,
            'Balance' : balance,
            'Transactions' : transactions,
            'Reward' : reward   
        }
    else:
        response = { "Messange" : "Mining Failed!!!"}
    return response

@app.route("/Transactions", methods =["GET"])
def new_Transactions():
    global balance
    recipient = input("Input Recipient :")
    amount = int(input("Input Amount :"))
    if amount > balance :
        print("Saldo tidak mencukupi")
        exit()
        
    new_Transactions = {
        "sender" : myWallet,
        "recipient" : recipient,
        "amount" : amount
    }
    
    prev_len_transactions = len(getlastBlock()["transactions"])
    getlastBlock()["transactions"].append(new_Transactions)
    if len(getlastBlock()["transactions"]) == prev_len_transactions+1:
        balance -= amount
        response = {
            'Messange' : 'Transactions Successfull!!!',
            'Transactions' : new_Transactions
        }
    else:
        response = {
            'Messange' : 'Transactions Failed!!!'
        }
    return response

@app.route("/add_note", methods= ["GET"])
def node_regis():
    url = input("Masukkan addreas: ")
    prev_nodes = len(nodes)
    nodes.append(url)
    if len(nodes) == prev_nodes+1:
        response = {
            'Messange' : 'Node added successfully!',
            'Node' : url
        }
    else:
        response = {
            'Messange' : 'Node failed!!!'
        }
    return response

@app.route("/sync", methods=["GET"])
def sync():
    update = update_blockchain()
    if update:
        response = {
            'Messange' : 'Blockchain Network Update'
        }
    else:
        response = {
            'Mesange' : 'Not need update'
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(sys.argv[1]))