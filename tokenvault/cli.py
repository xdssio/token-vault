import json
import os
import pyperclip
import typer
from typing import Optional
from importlib.metadata import version, PackageNotFoundError
import tokenvault
from tokenvault.config import CONSTANTS

app = typer.Typer()

PASSWORD_ERROR_MSG = (
    "Password is incorrect: please provide the correct password, "
    "set `TOKENVAULT_PASSWORD` or do not send a password if the vault is not encrypted"
)


def version_callback(value: bool):
    if value:
        try:
            typer.echo(version("tokenvault"))
        except PackageNotFoundError:
            typer.echo("unknown")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    pass


@app.command()
def init(
    path: str = typer.Argument("vault.db", help="Path to the vault file"),
    password: Optional[str] = typer.Option(
        None,
        "-p",
        "--password",
        help="Encrypt vault with this specific password.",
    ),
    generate_password: bool = typer.Option(
        False,
        "--generate-password",
        help="Generate a random password and encrypt the vault.",
    ),
):
    """Initialize a vault file in 'path' argument. Default is 'vault.db' with no encryption"""
    try:
        if generate_password and not password:
            password = tokenvault.TokenVault.generate_key().decode()
            pyperclip.copy(password)
            typer.echo(f"Generated password (copied to clipboard): {password}")
        elif not password:
            password = os.getenv(CONSTANTS.TOKENVAULT_PASSWORD)

        tokenvault.TokenVault().save(path, password=password)
        encrypt_message = (
            "and encrypted with password" if password else "and not encrypted"
        )
        typer.echo(f"Vault created at {path} {encrypt_message}")
    except ValueError:
        typer.echo(PASSWORD_ERROR_MSG)


@app.command()
def add(
    key: str = typer.Argument(..., help="Key to add to the vault"),
    path: str = typer.Argument("vault.db", help="Path to the vault file"),
    password: Optional[str] = typer.Option(
        None,
        "-p",
        "--password",
        help="If not provided and TOKENVAULT_PASSWORD is not set in environment, assume no password.",
    ),
    metadata: Optional[str] = typer.Option(
        None, "-m", "--metadata", help="Metadata for the key as json dict"
    ),
    echo_token: bool = typer.Option(
        False,
        "--echo-token",
        help="If True, echo the token to the console if generated.",
    ),
):
    """Add a new key to the vault and copy the token to the clipboard"""
    try:
        if metadata:
            metadata = json.loads(metadata)
        vault = tokenvault.TokenVault(path, password=password)
        token = vault.add(key, metadata=metadata)
        vault.save(path, password=password)
        pyperclip.copy(token)
        if echo_token:
            typer.echo(f"token: {token}")
    except ValueError:
        typer.echo(PASSWORD_ERROR_MSG)
    except json.JSONDecodeError:
        typer.echo("Metadata must be a valid json dict")


@app.command()
def remove(
    key: str = typer.Argument(..., help="Key to remove from the vault"),
    path: str = typer.Argument("vault.db", help="Path to the vault file"),
    password: Optional[str] = typer.Option(
        None,
        "-p",
        "--password",
        help="If not provided and TOKENVAULT_PASSWORD is not set in environment, assume no password.",
    ),
):
    """Remove a key from the vault"""
    try:
        vault = tokenvault.TokenVault(path, password=password)
        if vault.remove(key):
            vault.save(path, password=password)
            typer.echo(f"Removed key '{key}' from vault")
        else:
            typer.echo(f"Key '{key}' not found in vault")
    except ValueError:
        typer.echo(PASSWORD_ERROR_MSG)


@app.command()
def validate(
    token: str = typer.Argument(..., help="Token to validate"),
    path: str = typer.Argument("vault.db", help="Path to the vault file"),
    password: Optional[str] = typer.Option(
        None,
        "-p",
        "--password",
        help="If not provided and TOKENVAULT_PASSWORD is not set in environment, assume no password.",
    ),
):
    """Validate a token and return its metadata"""
    try:
        metadata = tokenvault.TokenVault(path, password=password).validate(token)
        if metadata is None:
            typer.echo("Token is not valid")
        else:
            typer.echo(json.dumps(metadata, indent=2))
    except ValueError:
        typer.echo(PASSWORD_ERROR_MSG)


@app.command()
def list(
    path: str = typer.Argument("vault.db", help="Path to the vault file"),
    password: Optional[str] = typer.Option(
        None,
        "-p",
        "--password",
        help="If not provided and TOKENVAULT_PASSWORD is not set in environment, assume no password.",
    ),
):
    """List existing keys in the vault"""
    try:
        vault = tokenvault.TokenVault(path, password=password)
        for key in vault.pool.keys():
            typer.echo(key)
    except ValueError:
        typer.echo(PASSWORD_ERROR_MSG)


@app.command()
def encrypted(path: str = typer.Argument("vault.db", help="Path to the vault file")):
    """Check if the vault is encrypted"""
    try:
        saved_password = os.environ.get(CONSTANTS.TOKENVAULT_PASSWORD)
        os.environ.pop(CONSTANTS.TOKENVAULT_PASSWORD, None)
        try:
            tokenvault.TokenVault(path, password=None)
            typer.echo("Vault is not encrypted")
        finally:
            if saved_password:
                os.environ[CONSTANTS.TOKENVAULT_PASSWORD] = saved_password
    except ValueError:
        typer.echo("Vault is encrypted")
