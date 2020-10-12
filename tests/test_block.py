from block import Block
from blockchain import Blockchain


def test_genesis_block_should_be_created():

    blockchain = Blockchain()

    assert isinstance(blockchain.last_block , Block)
    assert blockchain.last_block.hash is not None
    assert blockchain.last_block.index == 0
    assert len(blockchain._chain) == 1