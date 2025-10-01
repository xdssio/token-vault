import tempfile
import os
from typer.testing import CliRunner
from tokenvault.cli import app
import tokenvault
from importlib.metadata import version

runner = CliRunner()


def test_init_no_password():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    try:
        result = runner.invoke(app, ["init", tmp_path])
        assert result.exit_code == 0
        assert "Vault created" in result.stdout
        assert "not encrypted" in result.stdout
        assert os.path.exists(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_init_with_password():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    password = tokenvault.TokenVault.generate_key().decode()
    try:
        result = runner.invoke(app, ["init", tmp_path, "-p", password])
        assert result.exit_code == 0
        assert "Vault created" in result.stdout
        assert "encrypted with password" in result.stdout
        assert os.path.exists(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_add_and_validate():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    try:
        runner.invoke(app, ["init", tmp_path])

        add_result = runner.invoke(app, ["add", "test@example.com", tmp_path])
        assert add_result.exit_code == 0

        list_result = runner.invoke(app, ["list", tmp_path])
        assert list_result.exit_code == 0
        assert "test@example.com" in list_result.stdout
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_add_with_metadata():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    try:
        runner.invoke(app, ["init", tmp_path])

        add_result = runner.invoke(
            app, ["add", "user@example.com", tmp_path, "-m", '{"role": "admin"}']
        )
        assert add_result.exit_code == 0
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_remove():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    try:
        runner.invoke(app, ["init", tmp_path])
        runner.invoke(app, ["add", "test@example.com", tmp_path])

        remove_result = runner.invoke(app, ["remove", "test@example.com", tmp_path])
        assert remove_result.exit_code == 0
        assert "Removed key 'test@example.com'" in remove_result.stdout

        list_result = runner.invoke(app, ["list", tmp_path])
        assert "test@example.com" not in list_result.stdout
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_remove_nonexistent_key():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    try:
        runner.invoke(app, ["init", tmp_path])

        remove_result = runner.invoke(
            app, ["remove", "nonexistent@example.com", tmp_path]
        )
        assert remove_result.exit_code == 0
        assert "not found" in remove_result.stdout
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_list_empty_vault():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    try:
        runner.invoke(app, ["init", tmp_path])

        list_result = runner.invoke(app, ["list", tmp_path])
        assert list_result.exit_code == 0
        assert list_result.stdout.strip() == ""
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_encrypted_check():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    try:
        runner.invoke(app, ["init", tmp_path])

        encrypted_result = runner.invoke(app, ["encrypted", tmp_path])
        assert encrypted_result.exit_code == 0
        assert "not encrypted" in encrypted_result.stdout
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_encrypted_check_with_password():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    password = tokenvault.TokenVault.generate_key().decode()
    try:
        runner.invoke(app, ["init", tmp_path, "-p", password])

        encrypted_result = runner.invoke(app, ["encrypted", tmp_path])
        assert encrypted_result.exit_code == 0
        assert "Vault is encrypted" in encrypted_result.stdout
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_password_protection():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_path = tmp.name

    correct_password = tokenvault.TokenVault.generate_key().decode()
    wrong_password = tokenvault.TokenVault.generate_key().decode()
    try:
        runner.invoke(app, ["init", tmp_path, "-p", correct_password])

        add_result = runner.invoke(
            app, ["add", "test@example.com", tmp_path, "-p", correct_password]
        )
        assert add_result.exit_code == 0

        wrong_pass_result = runner.invoke(app, ["list", tmp_path, "-p", wrong_password])
        assert (
            "Password is incorrect" in wrong_pass_result.stdout
            or "incorrect" in wrong_pass_result.stdout.lower()
        )
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert version("tokenvault") in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.stdout
    assert "add" in result.stdout
    assert "remove" in result.stdout
    assert "validate" in result.stdout
    assert "list" in result.stdout
    assert "encrypted" in result.stdout
