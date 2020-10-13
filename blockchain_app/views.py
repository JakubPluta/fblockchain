import datetime
import json

import requests
from flask import render_template, redirect, request

from blockchain_app import app

def parse_timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')


NODE_ADDRESS = "http://127.0.0.1:8000"
posts = []


def get_posts():
    """Get chain from a blockchain node, parse the data and store it locally.
    """
    get_chain_address = f"{NODE_ADDRESS}/chain"
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["_transactions"]:
                tx["index"] = block["_index"]
                tx["hash"] = block["_previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    get_posts()
    return render_template('index.html',
                           title='YourNet: Decentralized '
                                 'content sharing',
                           posts=posts,
                           node_address=NODE_ADDRESS,
                           readable_time=parse_timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """Endpoint to create a new transaction via our app
    """
    post_content = request.form["content"]
    author = request.form["author"]
    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit transaction
    new_tx_address = f"{NODE_ADDRESS}/new_transaction"

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')