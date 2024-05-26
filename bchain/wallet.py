from pathlib import Path

import base64
from hashlib import sha256
from rsa import PublicKey, PrivateKey, newkeys

N_BITS = 512


class Wallet:
    def __init__(
            self,
            sk: PrivateKey,
    ) -> None:
        self.sk = sk
        self.pk = PublicKey(sk.n, sk.e)
        self.str_pk = f"{self.pk.n} {self.pk.e}"
        self.b64_address = base64.b64encode(sha256(self.str_pk.encode('ascii')).digest()).decode()

    def to_file(self, path: Path) -> None:
        with open(path, 'wb') as f:
            f.write(self.sk.save_pkcs1())

    @staticmethod
    def generate() -> 'Wallet':
        pk, sk = newkeys(N_BITS)
        return Wallet(sk)

    @staticmethod
    def from_file(p_secret_key: Path) -> 'Wallet':
        with open(p_secret_key, mode='rb') as f:
            key_data = f.read()
        sk = PrivateKey.load_pkcs1(key_data)
        return Wallet(sk)

