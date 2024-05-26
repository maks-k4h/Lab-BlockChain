import json
from pathlib import Path
from typing import List, Dict

from .block import Block
from .transaction import Transaction


class Chain:
    def __init__(
            self,
            blocks: List[Block]
    ) -> None:
        assert len(blocks) > 0

        self.blocks = blocks

    def verify(self) -> bool:
        assert len(self.blocks) > 0
        if not self.blocks[0].verify():
            return False
        for i in range(1, len(self.blocks)):
            prev_block = self.blocks[i - 1]
            block = self.blocks[i]
            if block.prev_block.b64_hash != prev_block.b64_hash:
                return False
            if not block.verify(check_pow=(i != len(self.blocks) - 1)):
                return False

        return True

    @property
    def last_block(self) -> Block:
        return self.blocks[-1]

    def add_block(self, block: Block) -> None:
        assert block.prev_block.b64_hash == self.last_block.b64_hash
        assert block.verify()
        self.blocks.append(block)

    def add_transaction(self, transaction: Transaction) -> None:
        if self.blocks[-1].verify(check_pow=True):  # last block is mined, create new one
            self.blocks.append(Block(prev_block=self.last_block))
        self.last_block.add_transaction(transaction)

    @staticmethod
    def new_chain(b64_miner: str) -> 'Chain':
        genesis_block = Block()
        genesis_block.mine(b64_miner)
        return Chain([genesis_block])

    def tolist(self) -> List:
        return [block.todict() for block in self.blocks]

    def to_file(self, path: Path) -> None:
        with open(path, 'w') as f:
            json.dump(self.tolist(), f, indent=2)

    @staticmethod
    def fromlist(l: List) -> 'Chain':
        blocks = [Block.fromdict(l[0])]
        for i in range(1, len(l)):
            block = Block.fromdict(l[i], prev_block=blocks[-1])
            blocks.append(block)
        return Chain(blocks)

    @staticmethod
    def from_file(path: Path) -> 'Chain':
        with open(path, 'r') as f:
            return Chain.fromlist(json.load(f))
