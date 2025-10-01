import os
import pathlib
import json
import base64
from collections import defaultdict
from typing import Optional, Dict, Any

import cryptography.fernet
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jwt
import uuid
from tokenvault.config import CONSTANTS
import importlib.metadata

__version__ = importlib.metadata.version("tokenvault")


class TokenVault:
    ALGORITHM = "RS256"
    DELIMITER = '=='

    def __init__(self, path: Optional[str] = None, password: Optional[str] = None):
        pool = defaultdict(dict)
        if path:
            pool = self.load_pool(path=path, password=password)
        self.pool = pool

    @classmethod
    def load_pool(cls, path: str, password: Optional[str] = None) -> Dict[str, bytes]:
        """Load and decrypt a vault from disk."""
        vault_path = pathlib.Path(path)
        if not vault_path.exists():
            raise FileNotFoundError(f"Vault file not found: {path}")
        data = vault_path.read_bytes()
        password = password or os.getenv(CONSTANTS.TOKENVAULT_PASSWORD)
        if password:
            try:
                data = cls.decrypt(data, password)
            except cryptography.fernet.InvalidToken:
                raise ValueError("Provided password is invalid")
        try:
            pool_json = json.loads(data)
            pool = defaultdict(dict)
            for key, value in pool_json.items():
                pool[key] = base64.b64decode(value)
            return pool
        except (json.JSONDecodeError, ValueError):
            raise ValueError(
                "File is encrypted: please provide password or set `TOKENVAULT_PASSWORD`"
            )

    def save(self, path: str, password: Optional[str] = None) -> str:
        """Encrypt and save the vault to disk."""
        password = password or os.getenv(CONSTANTS.TOKENVAULT_PASSWORD)
        pool_json = {
            key: base64.b64encode(value).decode("ascii")
            for key, value in self.pool.items()
        }
        data = json.dumps(pool_json).encode("utf-8")
        if password:
            data = self.encrypt(data, password)
        pathlib.Path(path).write_bytes(data)
        return path

    @classmethod
    def generate_key(cls) -> bytes:
        """Generate a random encryption key."""
        return Fernet.generate_key()

    @classmethod
    def encrypt(cls, data: bytes, key: Optional[bytes] = None) -> bytes:
        """Encrypt data using Fernet symmetric encryption."""
        return Fernet(key).encrypt(data)

    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> bytes:
        """Decrypt data using Fernet symmetric encryption."""
        return Fernet(key).decrypt(data)

    def add(self, key: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a token which can validate the key.
        :param key: This key could be verified using the generated token.
        :param metadata: any metadata you want provided at validation time
        :return: A Token which validates the key
        """
        if not key:
            raise ValueError("key cannot be empty")
        metadata = metadata.copy() if metadata else {}
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be of type dict")
        metadata[CONSTANTS.VALID] = str(uuid.uuid4())
        private_key = rsa.generate_private_key(
            public_exponent=CONSTANTS.RSA_PUBLIC_EXPONENT,
            key_size=CONSTANTS.RSA_KEY_SIZE,
        )
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.pool[key] = public_key_bytes
        return jwt.encode(metadata, private_key, algorithm=TokenVault.ALGORITHM) + f"{TokenVault.DELIMITER}{key}"

    def remove(self, key: str) -> bool:
        """Remove a key from the vault. Returns True if key existed, False otherwise."""
        return self.pool.pop(key, None) is not None

    def validate(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a token and return its metadata.
        :param token: The token to validate
        :return: None if the token is invalid, otherwise a dict with the metadata
        """
        split = token.split(TokenVault.DELIMITER, 1)
        if len(split) != 2 or split[1] not in self.pool:
            return None
        try:
            meta = jwt.decode(split[0], self.pool.get(split[1]), algorithms=[TokenVault.ALGORITHM])
            if meta.pop(CONSTANTS.VALID, None) is None:
                return None
            return meta
        except jwt.exceptions.PyJWTError:
            return None
