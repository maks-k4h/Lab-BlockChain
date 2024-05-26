import datetime
from typing import Optional

import rsa
import base64

from . import wallet


class Transaction:
    def __init__(
            self,
            b64_sender: str,
            b64_receiver: str,
            amount: int,
            b64_signature: Optional[str] = None,
            str_sender_pk: Optional[str] = None,
            timestamp: Optional[int] = None,
    ) -> None:
        assert amount > 0

        self.b64_sender = b64_sender
        self.b64_receiver = b64_receiver
        self._amount = amount
        self.b64_signature = b64_signature
        self.str_sender_pk = str_sender_pk
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def signable_str(self) -> str:
        return f"{self.b64_sender} {self.b64_receiver} {self.amount} {self.timestamp}"

    def sign(self, w: wallet.Wallet) -> None:
        assert self.b64_sender == w.b64_address, 'Only sender can sign transaction'

        self.b64_signature = base64.b64encode(rsa.sign(self.signable_str.encode(), w.sk, 'SHA-256')).decode()
        self.str_sender_pk = w.str_pk

    @property
    def is_signed(self) -> bool:
        return self.b64_signature is not None

    @property
    def sender_pk(self) -> rsa.PublicKey:
        return rsa.PublicKey(*[int(i) for i in self.str_sender_pk.split()])

    def verify_signature(self) -> bool:
        if not self.is_signed:
            return False
        try:
            rsa.verify(self.signable_str.encode(), base64.b64decode(self.b64_signature.encode()), self.sender_pk)
            return True
        except rsa.VerificationError:
            return False
