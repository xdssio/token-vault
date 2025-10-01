# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of TokenVault seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

**DO NOT** open a public issue for security vulnerabilities.

Instead, please report security issues by:
1. Opening a private security advisory on GitHub
2. Or emailing the maintainers directly (check GitHub profile for contact info)

### What to Include

Please include the following information in your report:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial Response:** Within 48 hours
- **Status Update:** Within 7 days
- **Fix Timeline:** Varies based on severity, typically within 30 days

### Security Best Practices

When using TokenVault:

1. **Always encrypt vaults in production**
   ```bash
   tv init vault.db --generate-password
   ```

2. **Never commit passwords or unencrypted vaults to version control**
   - Add `*.db` to `.gitignore` if not encrypting
   - Store passwords in environment variables or secret managers

3. **Use strong passwords for vault encryption**
   ```python
   password = TokenVault.generate_key()  # Uses cryptographically secure random
   ```

4. **Rotate tokens regularly**
   ```bash
   tv remove old@example.com vault.db
   tv add old@example.com vault.db --metadata='{"name": "User"}'
   ```

5. **Understand the limitations**
   - TokenVault is designed for small-scale applications
   - Not suitable for high-security production environments requiring compliance
   - Not a replacement for enterprise identity providers

### Known Limitations

- File-based storage is not suitable for high-concurrency scenarios
- No built-in token expiration (implement at application level if needed)
- No built-in rate limiting (implement at application level)
- Not designed for systems requiring HIPAA, GDPR strict compliance, or SOC2

### Security Features

- RSA-2048 asymmetric encryption for tokens
- Fernet symmetric encryption for vault storage
- JWT-based token validation
- No plaintext token storage 