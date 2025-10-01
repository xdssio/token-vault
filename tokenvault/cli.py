import json
import os
import pyperclip
import click
import tokenvault
from tokenvault.config import CONSTANTS
from functools import update_wrapper
from functools import update_wrapper


def handle_errors(f):
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        try:
            return ctx.invoke(f, *args, **kwargs)
        except ValueError as e:
            click.echo(
                f"Password is incorrect: please provide the correct password, set `TOKENVAULT_PASSWORD` or do not send a password if the vault is not encrypted")
        except json.JSONDecodeError:
            click.echo(f"Metadata must be a valid json dict")

    return update_wrapper(wrapper, f)


@click.group()
@click.version_option("1.0.0")
def main():
    pass


@main.command()
@click.argument("path", type=click.Path(exists=False), default="vault.db")
@click.option('-p', "--password", type=str,
              help=f"If not provided and TOKENVAULT_PASSWORD is not set in environment, will generate.")
@click.option('--no-password', is_flag=True, default=False, help=f"If True, generate a vault without encryption.")
@click.option("--echo-password", is_flag=True, default=False,
              help=f"If True, echo the password to the console if generated.")
@handle_errors
def init(path: str = "vault.db", password: str = None, no_password: bool = False, echo_password: bool = False):
    """Initialize a vault file in 'path' argument. Default is 'vault.db'"""
    if not no_password:
        password = password or os.getenv(CONSTANTS.TOKENVAULT_PASSWORD)
        if not password:
            password = tokenvault.TokenVault.generate_key().decode()
            pyperclip.copy(password)
        if echo_password:
            click.echo(f"password: {password}")
    tokenvault.TokenVault().save(path, password=password)
    encrypt_message = "and encrypted with password" if password else "and not encrypted"
    click.echo(f"Vault created at {path} {encrypt_message}")


@main.command()
@click.argument("key", type=str)
@click.argument("path", type=click.Path(exists=True), default="vault.db")
@click.option("-p", "--password", type=str, default=None,
              help=f"If not provided and TOKENVAULT_PASSWORD is not set in environment, assume no password.")
@click.option("-m", "--metadata", type=str, help=f"Metadata for the key as json dict")
@click.option("--echo-token", is_flag=True, default=False,
              help=f"If True, echo the token to the console if generated.")
@handle_errors
def add(key: str, path: str, password: str = None, metadata: str = None, echo_token: bool = False):
    """Add a new key to the vault and copy the token to the clipboard"""
    if metadata:
        metadata = json.loads(metadata)
    vault = tokenvault.TokenVault(path, password=password)
    token = vault.add(key, metadata=metadata)
    vault.save(path, password=password)
    pyperclip.copy(token)
    if echo_token:
        click.echo(f"token: {token}")


@main.command()
@click.argument("key", type=str)
@click.argument("path", type=click.Path(exists=True), default="vault.db")
@click.option("-p", "--password", type=str, default=None,
              help=f"If not provided and TOKENVAULT_PASSWORD is not set in environment, assume no password.")
@handle_errors
def remove(key: str, path: str, password: str = None):
    """Add a new key to the vault and copy the token to the clipboard"""

    vault = tokenvault.TokenVault(path, password=password)
    if vault.remove(key):
        vault.save(path, password=password)
        click.echo(f"Removed key '{key}' from vault")
    else:
        click.echo(f"Key '{key}' not found in vault")


@main.command()
@click.argument("token", type=str)
@click.argument("path", type=click.Path(exists=True), default="vault.db")
@click.option("-p", "--password", type=str, default=None,
              help=f"If not provided and TOKENVAULT_PASSWORD is not set in environment, assume no password.")
@handle_errors
def validate(token: str, path: str, password: str = None):
    """Add a new key to the vault and copy the token to the clipboard"""
    metadata = tokenvault.TokenVault(path, password=password).validate(token)
    if metadata is None:
        click.echo(f"Token is not valid")
    else:
        click.echo(metadata)


@main.command()
@click.argument("path", type=click.Path(exists=True), default="vault.db")
@click.option("-p", "--password", type=str, default=None,
              help=f"If not provided and TOKENVAULT_PASSWORD is not set in environment, assume no password.")
@handle_errors
def list(path: str, password: str = None):
    """List existing keys in the vault"""
    vault = tokenvault.TokenVault(path, password=password)
    for key in vault.pool.keys():
        click.echo(key)


@main.command()
@click.argument("path", type=click.Path(exists=True), default="vault.db")
def encrypted(path: str = "vault.db"):
    """Check if the vault is encrypted"""
    try:
        os.environ.pop(CONSTANTS.TOKENVAULT_PASSWORD, None)
        tokenvault.TokenVault(path, password=None)
        click.echo("Vault is not encrypted")
    except ValueError as e:
        click.echo("Vault is encrypted")


