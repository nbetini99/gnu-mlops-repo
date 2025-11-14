#!/bin/bash
# GitHub Secrets Setup using curl (no Python dependencies required)
# This script sets up GitHub Secrets using GitHub API with curl

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Repository information
REPO_OWNER="nbetini99"
REPO_NAME="gnu-mlops-repo"

# Secrets to set up
declare -A SECRETS=(
    ["DATABRICKS_HOST"]="https://dbc-5e289a33-a706.cloud.databricks.com"
    ["DATABRICKS_TOKEN"]="dapicb7282387c50cc9aa3e8e3d18378b5fd"
    ["DATABRICKS_WORKSPACE_PATH"]="/Users/nbatink@gmail.com/gnu-mlops/liveprod"
    ["DATABRICKS_EXPERIMENT_PATH"]="/Users/nbatink@gmail.com/gnu-mlops/experiments"
)

REQUIRED_SECRETS=("DATABRICKS_HOST" "DATABRICKS_TOKEN")

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GitHub Secrets Setup via API (curl method)            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠ GitHub Personal Access Token Required${NC}"
    echo ""
    echo "GitHub no longer accepts passwords for API access."
    echo "You need to create a Personal Access Token."
    echo ""
    echo "Steps to create a token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Click: 'Generate new token (classic)'"
    echo "3. Name: 'GNU MLOps Secrets Setup'"
    echo "4. Select scope: ✅ repo (Full control)"
    echo "5. Generate and copy the token"
    echo ""
    echo "Then run:"
    echo "  export GITHUB_TOKEN=your_token_here"
    echo "  ./setup_secrets_curl.sh"
    echo ""
    read -p "Do you want to create a token now? (y/n): " create_token
    if [[ "$create_token" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Opening GitHub token creation page..."
        open "https://github.com/settings/tokens/new"
        echo ""
        echo "After creating the token, run:"
        echo "  export GITHUB_TOKEN=your_token_here"
        echo "  ./setup_secrets_curl.sh"
        exit 0
    else
        exit 1
    fi
fi

GITHUB_TOKEN="$GITHUB_TOKEN"
echo -e "${GREEN}✓ GitHub token found${NC}"
echo ""

# Get public key
echo -e "${BLUE}📡 Getting repository public key...${NC}"
PUBLIC_KEY_RESPONSE=$(curl -s -H "Accept: application/vnd.github.v3+json" \
    -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/secrets/public-key")

if echo "$PUBLIC_KEY_RESPONSE" | grep -q '"key"'; then
    PUBLIC_KEY=$(echo "$PUBLIC_KEY_RESPONSE" | grep -o '"key":"[^"]*' | cut -d'"' -f4)
    KEY_ID=$(echo "$PUBLIC_KEY_RESPONSE" | grep -o '"key_id":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ Got public key: ${KEY_ID:0:8}...${NC}"
else
    echo -e "${RED}❌ Failed to get public key${NC}"
    echo "Response: $PUBLIC_KEY_RESPONSE"
    exit 1
fi

echo ""

# Note: Encrypting secrets with curl is complex (requires libsodium)
# We'll use Python for encryption but curl for API calls
echo -e "${BLUE}🔐 Setting up secrets...${NC}"
echo ""

# Check if Python is available for encryption
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Cannot encrypt secrets.${NC}"
    echo "Please use the Python script instead:"
    echo "  python3 setup_secrets_with_auth.py --token $GITHUB_TOKEN"
    exit 1
fi

# Try to encrypt using Python (will work if pynacl is available)
ENCRYPT_SCRIPT=$(cat << 'PYTHON_EOF'
import sys
import base64
try:
    from nacl import encoding, public
    public_key_str = sys.argv[1]
    secret_value = sys.argv[2]
    public_key_bytes = base64.b64decode(public_key_str)
    box = public.PublicKey(public_key_bytes)
    sealed_box = public.SealedBox(box)
    encrypted = sealed_box.encrypt(secret_value.encode('utf-8'))
    print(base64.b64encode(encrypted).decode('utf-8'))
except ImportError:
    print("ERROR: pynacl not installed", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
)

# Check if pynacl is available
if $PYTHON_CMD -c "import nacl" 2>/dev/null; then
    PYTHON_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ pynacl not available. Installing...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install pynacl --quiet 2>&1 | tail -1
        PYTHON_AVAILABLE=true
    else
        echo -e "${RED}❌ Cannot install pynacl. Please install it manually:${NC}"
        echo "  pip install pynacl"
        echo "Or use the Python script:"
        echo "  python3 setup_secrets_with_auth.py --token $GITHUB_TOKEN"
        exit 1
    fi
fi

# Set secrets
SUCCESS_COUNT=0
FAIL_COUNT=0

for SECRET_NAME in "${!SECRETS[@]}"; do
    SECRET_VALUE="${SECRETS[$SECRET_NAME]}"
    
    echo -n "Setting $SECRET_NAME... "
    
    # Encrypt secret
    ENCRYPTED_VALUE=$($PYTHON_CMD -c "$ENCRYPT_SCRIPT" "$PUBLIC_KEY" "$SECRET_VALUE" 2>&1)
    
    if [ $? -ne 0 ] || [[ "$ENCRYPTED_VALUE" == ERROR* ]]; then
        echo -e "${RED}❌ Failed to encrypt${NC}"
        ((FAIL_COUNT++))
        continue
    fi
    
    # Set secret via API
    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"encrypted_value\":\"$ENCRYPTED_VALUE\",\"key_id\":\"$KEY_ID\"}" \
        "https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/secrets/${SECRET_NAME}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "204" ]; then
        echo -e "${GREEN}✓ Success${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}❌ Failed (HTTP $HTTP_CODE)${NC}"
        if [ -n "$BODY" ]; then
            echo "  Response: $BODY"
        fi
        ((FAIL_COUNT++))
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Setup Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Success: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"
echo ""

# Check required secrets
REQUIRED_SET=true
for SECRET_NAME in "${REQUIRED_SECRETS[@]}"; do
    if [ $SUCCESS_COUNT -eq 0 ] || ! echo "$SECRET_NAME" | grep -q "$SECRET_NAME"; then
        REQUIRED_SET=false
    fi
done

if [ $SUCCESS_COUNT -gt 0 ] && [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ All secrets set successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Go to GitHub Actions tab"
    echo "  2. Trigger a workflow"
    echo "  3. Check logs for successful credential loading"
    echo ""
    echo "Verify secrets at:"
    echo "  https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/secrets/actions"
elif [ $SUCCESS_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some secrets failed to set${NC}"
    echo "   Please check the errors above"
else
    echo -e "${RED}❌ All secrets failed to set${NC}"
    echo "   Please check your GitHub token and permissions"
    exit 1
fi

echo ""

