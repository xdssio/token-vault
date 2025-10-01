# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-01

### Added
- FastAPI integration example in `examples/` directory
- SECURITY.md with security policy and best practices
- Comprehensive type hints for all public APIs
- GitHub Actions CI workflow for automated testing and linting
- Support for Python 3.8-3.12

### Changed
- Improved test coverage with proper assertions
- Bumped to v0.1.0 to indicate API stability

### Removed
- Unused `cloudpickle` dependency

## [0.0.2] - 2025

### Added
- CLI management tool (`tv` command)
- FastAPI integration examples
- Password-protected vault encryption
- Environment variable support (`TOKENVAULT_PASSWORD`)
- Comprehensive test suite

### Features
- Asymmetric encryption using RSA-2048
- JWT-based token validation
- Single-file vault storage
- Git-friendly encrypted file format

## [0.0.1] - 2025

### Added
- Initial release
- Core `TokenVault` class
- Basic token generation and validation
- Encryption/decryption utilities

[Unreleased]: https://github.com/xdssio/token-vault/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/xdssio/token-vault/releases/tag/v0.1.0
[0.0.2]: https://github.com/xdssio/token-vault/releases/tag/v0.0.2
[0.0.1]: https://github.com/xdssio/token-vault/releases/tag/v0.0.1 