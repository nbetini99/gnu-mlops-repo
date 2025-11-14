#!/bin/bash
# Quick setup script - Run this to set up GitHub Secrets

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     GitHub Secrets Setup - Quick Start                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Check/install dependencies
echo "Checking dependencies..."
python3 -c "import requests; from nacl import encoding, public" 2>/dev/null || {
    echo "Installing dependencies..."
    pip install requests pynacl --quiet
    echo "✓ Dependencies installed"
}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "STEP 1: Create GitHub Personal Access Token"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "GitHub requires a Personal Access Token (not password) for API access."
echo ""
echo "Please:"
echo "1. Go to: https://github.com/settings/tokens/new"
echo "2. Create a token with 'repo' scope"
echo "3. Copy the token"
echo ""
echo "Opening token creation page..."
open "https://github.com/settings/tokens/new" 2>/dev/null || echo "Please open: https://github.com/settings/tokens/new"
echo ""
read -p "Press Enter after creating the token..."

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "STEP 2: Enter Token and Set Up Secrets"
echo "═══════════════════════════════════════════════════════════════"
echo ""
read -sp "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Token cannot be empty"
    exit 1
fi

export GITHUB_TOKEN

echo ""
echo "Setting up secrets..."
python3 setup_secrets_with_auth.py --token "$GITHUB_TOKEN" --username "nbetini99"

