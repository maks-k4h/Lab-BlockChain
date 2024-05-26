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
            nonce: int = 0
    ) -> None:
        self._prev_block = prev_block
        self._transactions = transactions if transactions is not None else MerkleTree()
        self._b64_miner = b64_miner
        self._timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") if timestamp is None else timestamp
        self._nonce = nonce

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.add_transaction(transaction)

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
        assert not self.verify(check_pow=True), 'Block already mined!'
        self._b64_miner = b64_miner
        while self.b64_hash[:COMPLEXITY] != '0' * COMPLEXITY:
            self._nonce += random.randint(0x1, 0xFF)  # random step

    def verify(self, check_pow: bool = True) -> bool:
        # assuming previous blocks are valid, check the validity of current block
        if check_pow and self.b64_hash[:COMPLEXITY] != '0' * COMPLEXITY:
            return False
        if not self._transactions.verify():
            return False
        return True

    def todict(self) -> Dict:
        return {
            'hash': self.b64_hash,
            'timestamp': self._timestamp,
            'miner': self._b64_miner,
            'nonce': self._nonce,
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
