from blockchain import Blockchain
from block import Block
from time import time
from flask import Flask, request
import requests
import json

app = Flask(__name__)
blockchain = Blockchain()
peers = set() # Set of unique host addresses of participating members of the network


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
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


@app.route('/pending_tx')
def get_pending_tx():
    """ Get pending transactions with our data
    :return:
    """
    return json.dumps(blockchain._unconfirmed_transactions)


@app.route('/register_node', methods=['POST'])
def register_new_peers():
    """
    :return:
    """
    node_address = request.get_json()['node_address']
    if not node_address:
        return 'Invalid Data', 400
    peers.add(node_address)
    return get_chain()


def create_chain_from_dump(dump_data_of_chain):
    """
    :param dump_data_of_chain:
    :return:
    """
    blockchain = Blockchain()
    for index, block_data in enumerate(dump_data_of_chain):
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"])
        proof = block_data['hash']
        if index > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("Dumped data is manipulated!")

            "If index is 0  then it means, that we have there genesis block"
        else:
            blockchain.chain.append(block)
    return blockchain


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """Calls the register_node endpoint to register current node with the remote node specified in the
    request
    After that syncing blockchain with the remote node.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        return response.content, response.status_code


@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    """
    Adding block mined by other participants to the node's chain.
    The block is first verified by the node and then added to the chain.
    """
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)
    if not added:
        return "The block was discarded by the node", 400
    return "Block added to the chain", 201


def consensus():
    """Consnsus algorithm. If a longer valid chain is found, our chain is replaced with it.
    """
    global blockchain
    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True
    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)