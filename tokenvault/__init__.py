import os
import contextlib
import pathlib
from collections import defaultdict

import cryptography.fernet
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import cloudpickle
import jwt
import uuid
from tokenvault.config import CONSTANTS


class TokenVault:
    ALGORITHM = "RS256"
    DELIMITER = '=='

    def __init__(self, path: str = None, password: str = None):
        pool = defaultdict(dict)
        if path:
            pool = self.load_pool(path=path, password=password)
        self.pool = pool

    @classmethod
    def load_pool(cls, path, password: str = None):
        pool = pathlib.Path(path).read_bytes()
        password = password or os.getenv(CONSTANTS.TOKENVAULT_PASSWORD)
        if password:
            try:
                pool = cls.decrypt(pool, password)
            except cryptography.fernet.InvalidToken:
                raise ValueError("Provided password is invalid")
        del password
        with contextlib.suppress(cloudpickle.pickle.UnpicklingError):
            return cloudpickle.loads(pool)
        raise ValueError("File is encrypted: please provide password or set `TOKENVAULT_PASSWORD`")

    def save(self, path: str, password: str = None):
        password = password or os.getenv(CONSTANTS.TOKENVAULT_PASSWORD)
        data = cloudpickle.dumps(self.pool)
        if password:
            data = self.encrypt(data, password)
        pathlib.Path(path).write_bytes(data)
        return path

    @classmethod
    def generate_key(cls):
        return Fernet.generate_key()

    @classmethod
    def encrypt(cls, data: bytes, key: bytes = None):
        return Fernet(key).encrypt(data)

    @classmethod
    def decrypt(cls, data: bytes, key: bytes):
        return Fernet(key).decrypt(data)

    def add(self, key, metadata: dict = None):
        """
        Generate a token which can validate the key.
        :param key: This key could be verified using the generated token.
        :param metadata: and metadata you want provided at validation time
        :return: A Token which validates the key
        """
        metadata = metadata.copy() if metadata else {}
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be of type dict")
        metadata[CONSTANTS.VALID] = str(uuid.uuid4())
        private_key = rsa.generate_private_key(public_exponent=CONSTANTS.RAS_PUBLIC_EXPONENT,
                                               key_size=CONSTANTS.RSA_KEY_SIZE)
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.pool[key] = public_key_bytes
        return jwt.encode(metadata, private_key, algorithm=TokenVault.ALGORITHM) + f"{TokenVault.DELIMITER}{key}"

    def remove(self, key):
        return self.pool.pop(key, None) is not None

    def validate(self, token: str):
        """
        :param key: The
        :param token:
        :return: None if the key or token are invalid, otherwise a dict with the metadata
        """
        split = token.split(TokenVault.DELIMITER)
        if len(split) < 2 or split[1] not in self.pool:
            return None
        try:
            meta = jwt.decode(split[0], self.pool.get(split[1]), algorithms=[TokenVault.ALGORITHM])
            if meta.pop(CONSTANTS.VALID, None) is None:
                return None
            return meta
        except jwt.exceptions.PyJWTError:
            return None
