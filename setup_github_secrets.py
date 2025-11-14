#!/usr/bin/env python3
"""
GitHub Secrets Setup Script
This script helps you set up GitHub Secrets via the GitHub API

Requirements:
- GitHub Personal Access Token with 'repo' scope
- python3 with 'requests' library installed
- pip install requests pygithub (or use GitHub API directly)

Usage:
    python3 setup_github_secrets.py --token YOUR_GITHUB_TOKEN
"""

import os
import sys
import argparse
import base64
import json
from getpass import getpass

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found")
    print("Install it with: pip install requests")
    sys.exit(1)

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
OPTIONAL_SECRETS = ["DATABRICKS_WORKSPACE_PATH", "DATABRICKS_EXPERIMENT_PATH"]


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
        print("❌ Error: Invalid GitHub token or insufficient permissions")
        print("   Make sure your token has 'repo' scope")
        sys.exit(1)
    elif response.status_code == 403:
        print("❌ Error: Access forbidden")
        print("   Make sure you have admin access to the repository")
        sys.exit(1)
    else:
        print(f"❌ Error: Failed to get public key: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)


def encrypt_secret(public_key, secret_value):
    """Encrypt secret using repository public key"""
    try:
        from nacl import encoding, public
    except ImportError:
        print("❌ Error: 'pynacl' library not found")
        print("   Install it with: pip install pynacl")
        print("   Or use the manual setup method instead")
        sys.exit(1)
    
    public_key_bytes = base64.b64decode(public_key)
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
    
    if response.status_code == 204:
        return True
    elif response.status_code == 401:
        print(f"❌ Error: Invalid GitHub token for secret '{secret_name}'")
        return False
    elif response.status_code == 403:
        print(f"❌ Error: Access forbidden for secret '{secret_name}'")
        return False
    else:
        print(f"❌ Error: Failed to set secret '{secret_name}': {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def main():
    """Main function to set up GitHub Secrets"""
    parser = argparse.ArgumentParser(
        description="Set up GitHub Secrets for Databricks integration"
    )
    parser.add_argument(
        "--token",
        help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)",
        default=os.getenv("GITHUB_TOKEN")
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be set without actually setting secrets"
    )
    
    args = parser.parse_args()
    
    # Get GitHub token
    if not args.token:
        print("⚠ GitHub token not provided")
        print("   You can:")
        print("   1. Use --token flag: python3 setup_github_secrets.py --token YOUR_TOKEN")
        print("   2. Set GITHUB_TOKEN environment variable")
        print("   3. Use manual setup method (see GITHUB_SECRETS_SETUP_INSTRUCTIONS.md)")
        print("")
        token = getpass("Enter GitHub Personal Access Token (or press Ctrl+C to cancel): ")
    else:
        token = args.token
    
    print("\n" + "="*60)
    print("GitHub Secrets Setup for Databricks Integration")
    print("="*60)
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print("")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No secrets will be set")
        print("")
        print("Secrets that would be set:")
        for secret_name, secret_value in SECRETS.items():
            required = "✓ Required" if secret_name in REQUIRED_SECRETS else "○ Optional"
            print(f"  {required} {secret_name}: {secret_value}")
        print("")
        return
    
    # Get public key
    print("📡 Getting repository public key...")
    public_key_data = get_public_key(REPO_OWNER, REPO_NAME, token)
    public_key = public_key_data["key"]
    key_id = public_key_data["key_id"]
    print(f"✓ Got public key: {key_id[:8]}...")
    print("")
    
    # Set secrets
    print("🔐 Setting up secrets...")
    print("")
    
    results = {}
    for secret_name, secret_value in SECRETS.items():
        print(f"Setting {secret_name}...", end=" ")
        
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
    else:
        print("⚠️  Some required secrets failed to set")
        print("   Please check the errors above and try again")
        print("   Or use the manual setup method (see GITHUB_SECRETS_SETUP_INSTRUCTIONS.md)")
        sys.exit(1)
    
    print("")


if __name__ == "__main__":
    main()

