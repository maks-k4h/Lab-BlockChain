import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

from .block import Block
from .transaction import Transaction


MINING_REWARD = 100


class Chain:
    def __init__(
            self,
            blocks: List[Block]
    ) -> None:
        assert len(blocks) > 0

        self.blocks = blocks

    def verify(self) -> bool:
        assert len(self.blocks) > 0
        if not self.blocks[0].verify() or not self.blocks[0].is_mined:
            return False
        for i in range(1, len(self.blocks)):
            prev_block = self.blocks[i - 1]
            block = self.blocks[i]
            if block.prev_block.b64_hash != prev_block.b64_hash:
                return False
            if not block.verify():
                return False
            if (i != len(self.blocks) - 1) and not block.is_mined:
                return False

        return True

    @property
    def last_block(self) -> Block:
        return self.blocks[-1]

    @property
    def length(self) -> int:
        return len(self.blocks)

    def add_block(self, block: Block) -> None:
        assert block.prev_block.b64_hash == self.last_block.b64_hash
        assert block.verify()
        self.blocks.append(block)

    def add_transaction(self, transaction: Transaction) -> bool:
        if self.blocks[-1].is_mined:  # last block is mined, create new one
            self.blocks.append(Block(prev_block=self.last_block))
        # verify balance
        if self.calculate_balance(transaction.b64_sender)[0] - transaction.amount < 0:
            print('Not enough funds')
            return False
        self.last_block.add_transaction(transaction)
        return True

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

    @property
    def addresses(self) -> Set:
        res = set()
        for block in self.blocks:
            if block.is_mined:
                res.add(block.b64_miner)
            for transaction in block.transactions:
                res.add(transaction.b64_sender)
                res.add(transaction.b64_receiver)
        return res

    def calculate_balance(self, b64_address: str, omit_unverified: bool = True) -> Tuple[int, int, int]:
        # return balances: current, min, max
        # calculate balance based on verified transactions
        bal_cur = 0
        bal_min = 0
        bal_max = 0

        for block in self.blocks:
            if omit_unverified and not block.is_mined:  # unverified transactions
                break

            # transactions first
            for transaction in block.transactions:
                if transaction.b64_sender == b64_address:
                    bal_cur -= transaction.amount
                if transaction.b64_receiver == b64_address:
                    bal_cur += transaction.amount
                bal_min = min(bal_min, bal_cur)
                bal_max = max(bal_max, bal_cur)

            # mining happened after transactions
            if block.b64_miner == b64_address:
                bal_cur += MINING_REWARD
                if bal_min is None:
                    bal_min = bal_cur
                    bal_max = bal_cur
                bal_min = min(bal_min, bal_cur)
                bal_max = max(bal_max, bal_cur)

        return bal_cur, bal_min, bal_max

    def get_subchain(self, n: int) -> 'Chain':
        return Chain(self.blocks[:n])