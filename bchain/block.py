import base64
import datetime
import hashlib
import random
from typing import Optional, List, Dict

from .transaction import Transaction
from .merkle import MerkleTree


COMPLEXITY = 3


class Block:
    def __init__(
            self,
            b64_miner: Optional[str] = None,
            prev_block: Optional['Block'] = None,
            transactions: Optional[MerkleTree] = None,
            timestamp: str = None,
            nonce: int = None
    ) -> None:
        self._prev_block = prev_block
        self._transactions = transactions if transactions is not None else MerkleTree()
        self._b64_miner = b64_miner
        self._timestamp = timestamp
        self._nonce = nonce

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.add_transaction(transaction)

    @property
    def b64_miner(self) -> Optional[str]:
        return self._b64_miner

    @property
    def transactions(self) -> List[Transaction]:
        return self._transactions.transactions

    @property
    def prev_block(self) -> Optional['Block']:
        return self._prev_block

    @property
    def b64_hash(self) -> str:
        s = ''
        if self._prev_block is not None:
            s += self._prev_block.b64_hash
        else:
            s += '-'

        s += ' ' + self._transactions.b64_hash
        s += ' ' + self._timestamp
        s += ' ' + (self._b64_miner if self._b64_miner is not None else '-')
        s += ' ' + str(self._nonce)

        return base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()

    def mine(self, b64_miner: str) -> None:
        assert not self.is_mined
        self._nonce = 0
        self._timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self._b64_miner = b64_miner
        while not self.is_proved:
            self._nonce += random.randint(0x1, 0xFF)  # random step

    def verify(self) -> bool:
        # assuming previous blocks are valid, check the validity of current block
        if self.is_mined and not self.is_proved:
            return False
        if not self._transactions.verify():
            return False
        return True

    @property
    def is_mined(self) -> bool:
        return self._b64_miner is not None

    @property
    def is_proved(self) -> bool:
        return self.b64_hash[:COMPLEXITY] == '0' * COMPLEXITY

    def todict(self) -> Dict:
        return {
            'hash': self.b64_hash if self.is_mined else None,
            'timestamp': self._timestamp if self.is_mined else None,
            'miner': self._b64_miner if self.is_mined else None,
            'nonce': self._nonce if self.is_mined else None,
            'transactions': self._transactions.tolist(),
        }

    @staticmethod
    def fromdict(d: Dict, prev_block: Optional['Block'] = None) -> 'Block':
        return Block(
            b64_miner=d['miner'],
            timestamp=d['timestamp'],
            transactions=MerkleTree.fromlist(d['transactions']),
            nonce=d['nonce'],
            prev_block=prev_block
        )
