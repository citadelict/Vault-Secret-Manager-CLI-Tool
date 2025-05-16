# Vault Secret Manager CLI Tool

A Python CLI tool for managing secrets in HashiCorp Vault using HVAC client.

## Features

- Create and add new secrets
- Update existing secrets
- Delete secrets
- View all secrets for a project
- Project-based secret organization

## Prerequisites

- Python 3.x
- HashiCorp Vault server
- HVAC Python client (`pip install hvac`)

## Setup

1. Set environment variables:
```bash
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="your-root-token"
```

2. Install dependencies:
```bash
pip install hvac
```

## Usage

Run the script:
```bash
python vault_manager.py
```

Follow the interactive prompts to:
1. Enter your project ID
2. Choose operations (create, update, delete, view)
3. Manage your secrets

## Security Note

- Keep your Vault token secure
- Don't commit tokens to version control
- Use appropriate Vault policies in production