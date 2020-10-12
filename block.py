import hashlib
import json
from time import time


class Block:

    """We’ll store the hash of the block in a field inside our Block object,
    and it will act like a digital fingerprint (or signature) of data contained in it
    """

    def __init__(self, index, transactions, timestamp, previous_hash):
        """ Initialization of the Block class
        :param index: ID of the Block
        :param transactions: List of transactions
        :param timestamp: Time when block was generated
        """

        self._index = index
        self._transactions = transactions
        self._timestamp = timestamp
        self._previous_hash = previous_hash
        self._nonce = 0

    def calculate_hash(self):
        """

        A hash function is a function that takes data of any size and produces data of a fixed size from it (a hash),
        which is generally used to identify the input.

        """
        block = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block.encode()).hexdigest()

    @property
    def index(self):
        return self._index