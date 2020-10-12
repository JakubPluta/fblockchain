from blockchain import Blockchain
from block import Block
from time import time
from flask import Flask, request
import requests
import json

app = Flask(__name__)
blockchain = Blockchain()


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    """ Submit new transaction
    :return:
    """
    data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not data.get(field):
            return "Invalid transaction data", 404

    data["timestamp"] = time()
    blockchain.add_new_transaction(data)
    return "Success", 201


@app.route('/chain', methods=['GET'])
def get_chain():
    """ Returns a copy of our chain. Display all of the data
    """
    chain_data = []
    for block in blockchain._chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    """Method that's mine the unconfirmed transactions
    """
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)


@app.route('/pending_tx')
def get_pending_tx():
    """ Get pending transactions with our data
    :return:
    """
    return json.dumps(blockchain._unconfirmed_transactions)