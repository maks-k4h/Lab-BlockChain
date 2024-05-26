from typing import Optional, List, Dict

import hashlib
import base64

from .transaction import Transaction


class MerkleNode:
    def __init__(
            self,
            transaction: Transaction,
            prev_node: Optional['MerkleNode'] = None
    ) -> None:
        self.transaction = transaction
        self.prev_node = prev_node

    @property
    def b64_hash(self) -> str:
        assert self.transaction.is_signed

        s = self.transaction.signable_str
        s += ' ' + self.transaction.b64_signature
        s += ' ' + self.prev_node.b64_hash if self.prev_node is not None else '-'

        return base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()

    def todict(self) -> Dict:
        return {
            'hash': self.b64_hash,
            'timestamp': self.transaction.timestamp,
            'sender': self.transaction.b64_sender,
            'receiver': self.transaction.b64_receiver,
            'amount': self.transaction.amount,
            'sender_pk': self.transaction.str_sender_pk,
            'signature': self.transaction.b64_signature
        }

    @staticmethod
    def fromdict(d: Dict, prev_node: Optional['MerkleNode'] = None) -> 'MerkleNode':
        transaction = Transaction(
            b64_sender=d['sender'],
            b64_receiver=d['receiver'],
            amount=d['amount'],
            b64_signature=d['signature'],
            str_sender_pk=d['sender_pk'],
            timestamp=d['timestamp'],
        )
        return MerkleNode(transaction, prev_node)


class MerkleTree:
    def __init__(
            self,
            nodes: Optional[List[MerkleNode]] = None,
    ) -> None:
        self.nodes = nodes if nodes is not None else []

    def add_transaction(self, transaction: Transaction) -> None:
        node = MerkleNode(transaction, self.nodes[-1] if len(self.nodes) > 0 else None)
        self.nodes.append(node)

    @property
    def transactions(self) -> List[Transaction]:
        return [n.transaction for n in self.nodes]

    @property
    def b64_hash(self) -> str:
        if len(self.nodes) == 0:
            return base64.b64encode(b'-').decode()
        return base64.b64encode(self.nodes[-1].b64_hash.encode()).decode()

    def verify(self) -> bool:
        if len(self.nodes) == 0:
            return True
        if not self.nodes[0].transaction.verify_signature():
            return False
        for i in range(1, len(self.nodes)):
            prev_node = self.nodes[i - 1]
            node = self.nodes[i]
            if node.prev_node.b64_hash != prev_node.b64_hash:  # test connectivity
                return False
            if not node.transaction.verify_signature():  # test signatures
                return False
        return True

    def tolist(self) -> List:
        return [n.todict() for n in self.nodes]

    @staticmethod
    def fromlist(nodes: List) -> 'MerkleTree':
        if len(nodes) == 0:
            return MerkleTree()
        nodes_ = [MerkleNode.fromdict(nodes[0])]
        for node in nodes[1:]:
            nodes_.append(MerkleNode.fromdict(node, prev_node=nodes_[-1]))
        return MerkleTree(nodes_)
