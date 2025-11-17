# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within serverinspector, please send an
email to [EMAIL ADDRESS]. All security vulnerabilities will be promptly
addressed.

## Security Scanning

This repository uses automated security scanning to identify potential security issues:

### Automated Scans

The following security scans run automatically:

1. **Python Dependency Scanning** (Safety)
   - Scans Python dependencies for known vulnerabilities
   - Runs on every push to main, on pull requests, and weekly

2. **Static Code Analysis** (Bandit)
   - Analyzes Python code for common security issues
   - Focuses on security-specific concerns like injection, XSS, etc.

3. **CodeQL Analysis**
   - GitHub's semantic code analysis engine
   - Identifies vulnerabilities and coding errors

4. **Secret Scanning** (TruffleHog)
   - Detects accidentally committed secrets or credentials
   - Scans the entire git history

5. **Dependency Review**
   - Reviews dependency changes in pull requests
   - Identifies new vulnerabilities before they're merged

### Pre-commit Hooks

We use pre-commit hooks to catch issues before they are committed to the repository:

1. **Secret Detection** (detect-secrets)
   - Prevents committing API keys, tokens, and credentials
   - Maintains a baseline of allowed secrets

2. **Security Linting** (Bandit)
   - Checks Python code for common security vulnerabilities
   - Blocks commits with security issues

3. **Code Quality Checks**
   - Ensures consistent code formatting with Black and isort
   - Verifies Python syntax and style with Ruff
   - Enforces documentation standards with interrogate

To set up pre-commit hooks for local development:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Generate/update the secrets baseline (first time only)
detect-secrets scan > .secrets.baseline

# To update an existing baseline
rm .secrets.baseline && detect-secrets scan > .secrets.baseline
```

### Running Scans Locally

You can run these security scans locally:

```bash
# Install security tools
pip install bandit safety

# Scan dependencies
safety check

# Scan code
bandit -r src/

# For more detailed output
bandit -r src/ -f json -o security-results.json
```

## Security Best Practices

When contributing to serverinspector, please follow these security best practices:

1. **No hardcoded secrets** - Use environment variables for sensitive data
2. **Input validation** - Validate all user inputs
3. **Command injection** - Be careful when executing system commands with user input
4. **Dependency management** - Keep dependencies updated

## Dependency Updates

We use GitHub's Dependabot to keep dependencies updated. Security updates are
automatically created as pull requests.
