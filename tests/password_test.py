from tempfile import NamedTemporaryFile
from tokenvault import TokenVault
import pytest
import os
from tokenvault.config import CONSTANTS


def test_vault_persistence():
    vault = TokenVault()
    metadata = {"name": 'Alon'}
    alon_token = vault.add('user@gmail.com', metadata)
    file = NamedTemporaryFile()
    vault.save(file.name)
    assert TokenVault(file.name).validate(alon_token) == metadata


def test_vault_persistence_password():
    vault = TokenVault()
    password = vault.generate_key()
    metadata = {"name": 'Alon'}
    alon_token = vault.add('user@gmail.com', metadata)
    file = NamedTemporaryFile()
    vault.save(file.name, password=password)
    with pytest.raises(ValueError):
        TokenVault(file.name)
    assert TokenVault(file.name, password=password).validate(alon_token) == metadata


def test_vault_password():
    password = TokenVault.generate_key()
    vault = TokenVault(password=password)
    metadata = {"name": 'Alon'}
    alon_token = vault.add('user@gmail.com', metadata)
    file = NamedTemporaryFile()
    vault.save(file.name, password=password)
    assert TokenVault(file.name, password=password).validate(alon_token) == metadata


def test_environment_password():
    os.environ[CONSTANTS.TOKENVAULT_PASSWORD] = TokenVault.generate_key().decode()
    vault = TokenVault()
    metadata = {"name": 'Alon'}
    alon_token = vault.add('user@gmail.com', metadata)

    file = NamedTemporaryFile()
    vault.save(file.name)
    assert TokenVault(file.name).validate(alon_token) == metadata
    with pytest.raises(ValueError):
        TokenVault(file.name, password=TokenVault.generate_key())
    del os.environ[CONSTANTS.TOKENVAULT_PASSWORD]
    with pytest.raises(ValueError):
        TokenVault(file.name)


def test_vault_password_wrong():
    password = TokenVault.generate_key()
    vault = TokenVault(password=password)
    file = NamedTemporaryFile()
    vault.save(file.name, password=password)
    with pytest.raises(ValueError):
        TokenVault(file.name, password=TokenVault.generate_key())
