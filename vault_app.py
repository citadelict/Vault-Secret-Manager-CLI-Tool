import hvac
import os

# Vault client config
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "your-root-token")

client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

if not client.is_authenticated():
    raise Exception("Vault auth failed. Check VAULT_TOKEN and VAULT_ADDR.")

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

def create_or_update(project_id):
    existing = read_secrets(project_id)
    while True:
        key = input("Enter key (or 'done' to finish): ").strip()
        if key.lower() == "done":
            break
        value = input(f"Enter value for '{key}': ").strip()
        existing[key] = value
        write_secrets(project_id, existing)
        print(f"✓ '{key}' set.")

def update_key(project_id):
    existing = read_secrets(project_id)
    key = input("Key to update: ").strip()
    if key not in existing:
        print("⚠ Key does not exist. Use create option instead.")
        return
    value = input(f"New value for '{key}': ").strip()
    existing[key] = value
    write_secrets(project_id, existing)
    print(f"✓ '{key}' updated.")

def delete_key(project_id):
    existing = read_secrets(project_id)
    key = input("Key to delete: ").strip()
    if key in existing:
        del existing[key]
        write_secrets(project_id, existing)
        print(f"✓ '{key}' deleted.")
    else:
        print("⚠ Key not found.")

def view_secrets(project_id):
    secrets = read_secrets(project_id)
    if not secrets:
        print("No secrets found.")
    else:
        for k, v in secrets.items():
            print(f"{k} = {v}")

def main():
    print("🔐 Vault Secret Manager")
    project_id = input("Enter project ID (e.g., project-xyz): ").strip()

    while True:
        print("\nChoose an option:")
        print("1. Create or add new secrets")
        print("2. Update an existing secret key")
        print("3. Delete a secret key")
        print("4. View current secrets")
        print("5. Exit")

        choice = input("Select (1-5): ").strip()

        if choice == "1":
            create_or_update(project_id)
        elif choice == "2":
            update_key(project_id)
        elif choice == "3":
            delete_key(project_id)
        elif choice == "4":
            view_secrets(project_id)
        elif choice == "5":
            print("Bye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
