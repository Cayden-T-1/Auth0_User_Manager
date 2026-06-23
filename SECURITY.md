# 3. Auth0_User_Manager — SECURITY.md

````markdown
# Security Policy

## Project Security Scope

This repository contains scripts or tooling for managing Auth0 users through the Auth0 Management API.

Because user management operations can involve identity data, Management API credentials, and privileged tenant actions, this repository must be handled as security-sensitive.

## Reporting a Security Issue

If you discover a security issue in this repository, do not open a public GitHub issue.

Report the issue privately to the repository owner or maintainer.

Please include:

- Repository name
- File or script affected
- Description of the issue
- Steps to reproduce, if applicable
- Whether Auth0 credentials, Management API tokens, user data, or tenant details may be exposed
- Recommended remediation, if known

## Sensitive Data That Must Not Be Committed

Do not commit:

- Auth0 client secrets
- Auth0 Management API client secrets
- Auth0 Management API access tokens
- Hardcoded tenant credentials
- `.env` files
- User data exports
- Passwords
- Private keys
- Customer data
- Production tenant details unless explicitly approved

## Credential Handling

Auth0 credentials must not be hardcoded in Python files or other source files.

Use environment variables or an approved secret manager for:

- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `AUTH0_AUDIENCE`
- `AUTH0_MANAGEMENT_API_TOKEN`

Example safe pattern:

```python
import os

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

if not AUTH0_DOMAIN or not CLIENT_ID or not CLIENT_SECRET:
    raise SystemExit("Missing required Auth0 environment variables.")
````

## User Data Protection

Do not commit real user data, including:

* Email addresses
* Names
* Phone numbers
* User IDs
* MFA enrollment data
* Profile metadata
* Application metadata
* Passwords or temporary passwords

Use fake sample users for demos and documentation.

## If a Secret Is Accidentally Committed

If an Auth0 secret, token, credential, or user data file is committed:

1. Treat the credential or data exposure as a security incident.
2. Rotate the exposed Auth0 credential immediately.
3. Remove the secret or data from the repository.
4. Review Git history for prior exposure.
5. Review Auth0 logs for suspicious Management API activity.
6. Confirm whether any user data was exposed.
7. Notify the project owner or maintainer.

Redacting the file is not enough if a real credential was committed. The credential must be rotated.

## Secure Coding Expectations

Before committing changes:

* Do not hardcode secrets.
* Do not log tokens or client secrets.
* Do not print full Management API responses if they contain user data.
* Use least-privilege Management API scopes.
* Validate input files before processing.
* Avoid destructive operations unless clearly documented.
* Include dry-run mode where possible.
* Document required Auth0 scopes.

## Supported Use

This repository is intended for controlled Auth0 user management, training, and internal automation unless otherwise stated.

Security-sensitive changes should be reviewed before being merged.