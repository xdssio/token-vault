from tokenvault import TokenVault


def test_add_validate():
    vault = TokenVault()
    token = vault.add("test@gmail.com", {"test": "test"})
    assert vault.validate(token) == {"test": "test"}


def test_keys():
    vault = TokenVault()
    token1 = vault.add("test@gmail.com", {"test": "test"})
    token2 = vault.add("test2@gmail.com", {"test2": "test2"})
    assert vault.validate(token1) == {"test": "test"}
    assert vault.validate(token2) == {"test2": "test2"}

    assert vault.remove("test@gmail.com")
    assert vault.validate(token1) is None

    assert vault.add("test@gmail.com", {"test": "test"}) != token1
