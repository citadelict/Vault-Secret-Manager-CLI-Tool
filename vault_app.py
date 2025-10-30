import hvac
import os
import json
import logging

# ──────────────────────────────────────
# Vault client config (from env vars)
# ──────────────────────────────────────
VAULT_ADDR  = os.getenv("VAULT_ADDR")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

if not VAULT_ADDR or not VAULT_TOKEN:
    raise Exception("VAULT_ADDR and VAULT_TOKEN must be set in environment variables")

client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
if not client.is_authenticated():
    raise Exception("Vault auth failed. Check VAULT_TOKEN and VAULT_ADDR.")

# ──────────────────────────────────────
# Your existing functions (unchanged)
# ──────────────────────────────────────
def full_path(project_id):
    return f"{project_id}/env"

def read_secrets(project_id):
    try:
        response = client.secrets.kv.v2.read_secret_version(path=full_path(project_id))
        return response["data"]["data"]
    except hvac.exceptions.InvalidPath:
        return {}

def write_secrets(project_id, secrets):
    client.secrets.kv.v2.create_or_update_secret(
        path=full_path(project_id),
        secret=secrets
    )

# ──────────────────────────────────────
# NEW: Lambda handler (API-style)
# ──────────────────────────────────────
def handler(event, context):
    """
    Expected event:
    {
      "action": "read|write|update|delete|view",
      "project_id": "my-app",
      "key": "DB_PASSWORD",           # optional
      "value": "s3cr3t"               # optional
    }
    """
    logging.getLogger().setLevel(logging.INFO)
    try:
        action = event.get("action")
        project_id = event.get("project_id")

        if not project_id:
            return {"statusCode": 400, "body": json.dumps({"error": "project_id required"})}

        if action == "read":
            secrets = read_secrets(project_id)
            return {"statusCode": 200, "body": json.dumps(secrets)}

        elif action == "write":
            key = event.get("key")
            value = event.get("value")
            if not key or not value:
                return {"statusCode": 400, "body": json.dumps({"error": "key and value required"})}
            secrets = read_secrets(project_id)
            secrets[key] = value
            write_secrets(project_id, secrets)
            return {"statusCode": 200, "body": json.dumps({"message": f"{key} set"})} 

        elif action == "update":
            key = event.get("key")
            value = event.get("value")
            if not key or not value:
                return {"statusCode": 400, "body": json.dumps({"error": "key and value required"})}
            secrets = read_secrets(project_id)
            if key not in secrets:
                return {"statusCode": 404, "body": json.dumps({"error": "key not found"})}
            secrets[key] = value
            write_secrets(project_id, secrets)
            return {"statusCode": 200, "body": json.dumps({"message": f"{key} updated"})}

        elif action == "delete":
            key = event.get("key")
            if not key:
                return {"statusCode": 400, "body": json.dumps({"error": "key required"})}
            secrets = read_secrets(project_id)
            if key in secrets:
                del secrets[key]
                write_secrets(project_id, secrets)
                return {"statusCode": 200, "body": json.dumps({"message": f"{key} deleted"})}
            else:
                return {"statusCode": 404, "body": json.dumps({"error": "key not found"})}

        elif action == "view":
            secrets = read_secrets(project_id)
            return {"statusCode": 200, "body": json.dumps(secrets)}

        else:
            return {"statusCode": 400, "body": json.dumps({"error": "invalid action"})}

    except Exception as e:
        logging.error(str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

# ──────────────────────────────────────
# Keep CLI for local testing (optional)
# ──────────────────────────────────────
if __name__ == "__main__":
    # Fallback to CLI when run locally
    import sys
    if len(sys.argv) > 1:
        print("CLI mode not supported in Lambda. Use handler(event).")
    else:
        print("Run locally with: python vault_app.py")
