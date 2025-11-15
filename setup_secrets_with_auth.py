#!/usr/bin/env python3
"""
GitHub Secrets Setup Script with Authentication
This script sets up GitHub Secrets using GitHub API

Note: GitHub requires Personal Access Token (not password) for API access
"""

import os
import sys
import base64
import json
import getpass

try:
    import requests
except ImportError:
    print("Installing requests library...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', '--quiet'])
    import requests

try:
    from nacl import encoding, public
except ImportError:
    print("Installing pynacl library...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pynacl', '--quiet'])
    from nacl import encoding, public

# Repository information
REPO_OWNER = "nbetini99"
REPO_NAME = "gnu-mlops-repo"

# Secrets to set up
SECRETS = {
    "DATABRICKS_HOST": "https://dbc-5e289a33-a706.cloud.databricks.com",
    "DATABRICKS_TOKEN": "dapicb7282387c50cc9aa3e8e3d18378b5fd",
    "DATABRICKS_WORKSPACE_PATH": "/Users/nbatink@gmail.com/gnu-mlops/liveprod",
    "DATABRICKS_EXPERIMENT_PATH": "/Users/nbatink@gmail.com/gnu-mlops/experiments"
}

REQUIRED_SECRETS = ["DATABRICKS_HOST", "DATABRICKS_TOKEN"]


def get_public_key(owner, repo, token):
    """Get repository public key for encryption"""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        print("❌ Error: Invalid GitHub token")
        print("   The token may be expired or have insufficient permissions")
        return None
    elif response.status_code == 403:
        print("❌ Error: Access forbidden")
        print("   Make sure you have admin access to the repository")
        return None
    else:
        print(f"❌ Error: Failed to get public key: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def encrypt_secret(public_key_str, secret_value):
    """Encrypt secret using repository public key"""
    public_key_bytes = base64.b64decode(public_key_str)
    box = public.PublicKey(public_key_bytes)
    sealed_box = public.SealedBox(box)
    encrypted = sealed_box.encrypt(secret_value.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def set_secret(owner, repo, secret_name, encrypted_value, key_id, token):
    """Set a secret in GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    data = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    # GitHub returns 204 (No Content) or 201 (Created) for successful secret creation
    if response.status_code in [204, 201]:
        return True
    elif response.status_code == 401:
        print(f"❌ Error: Invalid GitHub token for secret '{secret_name}'")
        return False
    elif response.status_code == 403:
        print(f"❌ Error: Access forbidden for secret '{secret_name}'")
        return False
    else:
        print(f"❌ Error: Failed to set secret '{secret_name}': {response.status_code}")
        if response.text:
            print(f"   Response: {response.text}")
        return False


def create_personal_access_token_instructions():
    """Print instructions for creating a Personal Access Token"""
    print("\n" + "="*60)
    print("GitHub Personal Access Token Required")
    print("="*60)
    print("\nGitHub no longer accepts passwords for API access.")
    print("You need to create a Personal Access Token.\n")
    print("Steps to create a token:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click: 'Generate new token (classic)'")
    print("3. Give it a name: 'GNU MLOps Secrets Setup'")
    print("4. Select scopes:")
    print("   ✅ repo (Full control of private repositories)")
    print("5. Click: 'Generate token'")
    print("6. Copy the token (you won't see it again!)")
    print("\nThen run this script again with:")
    print("  python3 setup_secrets_with_auth.py --token YOUR_TOKEN")
    print("\nOr set it as environment variable:")
    print("  export GITHUB_TOKEN=YOUR_TOKEN")
    print("  python3 setup_secrets_with_auth.py")
    print("")


def main():
    """Main function to set up GitHub Secrets"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Set up GitHub Secrets for Databricks integration"
    )
    parser.add_argument(
        "--token",
        help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)",
        default=os.getenv("GITHUB_TOKEN")
    )
    parser.add_argument(
        "--username",
        help="GitHub username (for reference only)",
        default="nbetini99"
    )
    
    args = parser.parse_args()
    
    # Get GitHub token
    token = args.token
    
    if not token:
        print("\n" + "="*60)
        print("GitHub Personal Access Token Required")
        print("="*60)
        print("\n⚠️  GitHub requires a Personal Access Token (not password) for API access.")
        print("\nTo create a token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click: 'Generate new token (classic)'")
        print("3. Name: 'GNU MLOps Secrets Setup'")
        print("4. Select scope: ✅ repo (Full control)")
        print("5. Generate and copy the token")
        print("\nThen run:")
        print("  python3 setup_secrets_with_auth.py --token YOUR_TOKEN")
        print("\nOr set environment variable:")
        print("  export GITHUB_TOKEN=YOUR_TOKEN")
        print("  python3 setup_secrets_with_auth.py")
        print("")
        create_personal_access_token_instructions()
        sys.exit(1)
    
    print("\n" + "="*60)
    print("GitHub Secrets Setup for Databricks Integration")
    print("="*60)
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print(f"Username: {args.username}")
    print("")
    
    # Get public key
    print("📡 Getting repository public key...")
    public_key_data = get_public_key(REPO_OWNER, REPO_NAME, token)
    
    if not public_key_data:
        print("\n❌ Failed to get public key. Please check:")
        print("   1. Token is valid and not expired")
        print("   2. Token has 'repo' scope")
        print("   3. You have admin access to the repository")
        sys.exit(1)
    
    public_key = public_key_data["key"]
    key_id = public_key_data["key_id"]
    print(f"✓ Got public key: {key_id[:8]}...")
    print("")
    
    # Set secrets
    print("🔐 Setting up secrets...")
    print("")
    
    results = {}
    for secret_name, secret_value in SECRETS.items():
        print(f"Setting {secret_name}...", end=" ", flush=True)
        
        # Encrypt secret
        try:
            encrypted_value = encrypt_secret(public_key, secret_value)
        except Exception as e:
            print(f"❌ Failed to encrypt: {e}")
            results[secret_name] = False
            continue
        
        # Set secret
        success = set_secret(REPO_OWNER, REPO_NAME, secret_name, encrypted_value, key_id, token)
        
        if success:
            print(f"✓ Success")
            results[secret_name] = True
        else:
            print(f"❌ Failed")
            results[secret_name] = False
    
    print("")
    print("="*60)
    print("Setup Summary")
    print("="*60)
    print("")
    
    # Print results
    for secret_name, success in results.items():
        status = "✓ Success" if success else "❌ Failed"
        required = "Required" if secret_name in REQUIRED_SECRETS else "Optional"
        print(f"  {status} {secret_name} ({required})")
    
    print("")
    
    # Check if all required secrets were set
    required_set = all(results.get(name, False) for name in REQUIRED_SECRETS)
    
    if required_set:
        print("✅ All required secrets set successfully!")
        print("")
        print("Next steps:")
        print("  1. Go to GitHub Actions tab")
        print("  2. Trigger a workflow")
        print("  3. Check logs for successful credential loading")
        print("")
        print("Verify secrets at:")
        print(f"  https://github.com/{REPO_OWNER}/{REPO_NAME}/settings/secrets/actions")
    else:
        print("⚠️  Some required secrets failed to set")
        print("   Please check the errors above and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()

