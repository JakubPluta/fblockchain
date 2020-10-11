import hashlib
import json
from time import time


class Blockchain:
    """
        Each block should contain within itself, hash of the previous Block.
        It's an idea that gives immutability for block chain. It's impossible to break a block chain by hackers.
    """

    def __init__(self):
        self._chain = []
        self._current_transactions = []

    def new_block(self, proof, previous_hash=None):
        """
            Creates a new block in our block chain.

        :param proof: PoW proof
        :param previous_hash: previous block hash
        :return: dict with new block with keys
            block.keys()  = 'index',timestamp','transactions', 'proof', 'previous_hash'

        """

        block = {
            'index': len(self._chain) + 1,
            'timestamp': time(),
            'transactions': self._current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self._chain[-1]),
        }

        """Reset our list of transactions, set it to empty list"""
        self._current_transactions = list()

        """add created block to our chain list"""
        self._chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: [int,float]) -> int:
        """
            Adding transactions to a Block.
                * we add a transaction to the our list, our method
                returns the index of the block which the transaction
                will be added to—the next one to be mined.


        :param sender: Address of the sender
        :param recipient: Address of the recipient
        :param amount: Amount of transaction (int, float)
        :return: int - > Index of the block
        """

        self._current_transactions.append(
            {
                'sender': sender,
                'recipient': recipient,
                'amount': amount

            }
        )
        return self.last_block['index'] + 1

    @staticmethod
    def create_hash(block):
        """
        Create SHA-256 hash of a block
        :param block: dict
        :return: hash
        """

        """Convert block dict into string, and sort to have consistency in hashes"""
        block = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block).hexdigest()

    @property
    def last_block(self):
        return self._chain[-1]