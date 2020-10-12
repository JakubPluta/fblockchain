from time import time
from block import Block


class Blockchain:
    """
        Each block should contain within itself, hash of the previous Block.
        It's an idea that gives immutability for block chain. It's impossible to break a block chain by hackers.

        The number of zeroes specified in the constraint determines the difficulty of our proof of work algorithm
        (the greater the number of zeroes, the harder it is to figure out the nonce).

    """

    DIFFICULTY = 2

    def __init__(self):
        self._chain = []
        self._unconfirmed_transactions = []
        self.generate_genesis_block()

    @property
    def chain(self):
        return self._chain

    def generate_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], time(), "0")
        genesis_block.hash = genesis_block.calculate_hash()
        self._chain.append(genesis_block)

    def add_block(self, block: Block, proof):
        """Adds block to the chain after verification.
        Verification includes:
            * Checking if the proof is valid.
            * The previous_hash referred in the block and the hash of a latest block in
        """

        previous_hash = self.last_block.hash

        if previous_hash != block._previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self._chain.append(block)
        return True

    def add_new_transaction(self, transaction):
        self._unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        Interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        :return:
        """
        if not self._unconfirmed_transactions:
            return False
        last_block = self.last_block

        new_block = Block(index=last_block._index + 1,
                          transactions=self._unconfirmed_transactions,
                          timestamp=time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self._unconfirmed_transactions = []
        return new_block._index

    @property
    def last_block(self):
        """
        :return: Most recent block in the chain. Note that the chain will always consist
        of at least one block (i.e., genesis block)
        """
        return self._chain[-1]

    @staticmethod
    def proof_of_work(block):
        """
        If we change the previous block, the hashes of all the blocks that follow can be re-computed quite easily to
        create a different valid blockchain.To prevent this, we need to create asymmetry in efforts of hash functions.

        Instead of accepting any hash for the block, we need to add some constraint to it.

        Constraint:  our hash should start with 'n leading zeroes' where n can be any positive integer.
        :param block:
        :return:


        A nonce is a number that we can keep on changing until we get a hash that satisfies our constraint. 

        The nonce satisfying the constraint serves as proof that some computation has been performed.
        """

        block._nonce = 0
        computed_hash = block.calculate_hash()

        while not computed_hash.startswith('0' * Blockchain.DIFFICULTY):
            block._nonce += 1
            computed_hash = block.calculate_hash()
        return computed_hash

    @staticmethod
    def is_valid_proof(block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.DIFFICULTY) and
                block_hash == block.calculate_hash())

    def check_chain_validity(cls, chain):
        """
        A helper method to check if the entire blockchain is valid.
        """
        result = True
        previous_hash = "0"

        # Iterate through every block
        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")
            if not cls.is_valid_proof(block, block.hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break
            block.hash, previous_hash = block_hash, block_hash
        return result

