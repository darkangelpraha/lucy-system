#!/bin/bash
# 1PASSWORD AUTO-SETUP
# Pulls credentials from 1Password AI vault automatically

set -e

echo "🔐 Lucy - 1Password Auto Setup"
echo "==============================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if op CLI is installed
if ! command -v op &> /dev/null; then
    echo "❌ 1Password CLI not found!"
    echo ""
    echo "Install:"
    echo "  brew install 1password-cli"
    echo ""
    echo "Or download from: https://1password.com/downloads/command-line/"
    exit 1
fi

echo "✅ 1Password CLI found"
echo ""

# Check if signed in
if ! op account list &> /dev/null; then
    echo "🔑 Signing in to 1Password..."
    eval $(op signin)
fi

echo "✅ Signed in to 1Password"
echo ""

# Vault name
VAULT="AI"

echo "📥 Fetching credentials from vault '$VAULT'..."
echo ""

# Function to get credential
get_cred() {
    local item_name=$1
    local field_name=$2
    
    echo "  ↓ $item_name"
    op item get "$item_name" --vault "$VAULT" --fields "$field_name" 2>/dev/null || echo ""
}

# Fetch credentials
ANTHROPIC_API_KEY=$(get_cred "Anthropic" "api_key")
SUPABASE_URL=$(get_cred "Supabase" "url")
SUPABASE_KEY=$(get_cred "Supabase" "api_key")
NOTION_API_KEY=$(get_cred "Notion" "api_key")
LINEAR_API_KEY=$(get_cred "Linear" "api_key")
TODOIST_API_TOKEN=$(get_cred "Todoist" "api_token")
GMAIL_CLIENT_ID=$(get_cred "Gmail API" "client_id")
GMAIL_CLIENT_SECRET=$(get_cred "Gmail API" "client_secret")
GMAIL_REFRESH_TOKEN=$(get_cred "Gmail API" "refresh_token")

echo ""
echo "✅ Credentials fetched"
echo ""

# Create .env file
cat > "$SCRIPT_DIR/.env" << EOF
# LUCY SYSTEM - ENVIRONMENT VARIABLES
# Auto-generated from 1Password AI vault
# Generated: $(date)

# Anthropic API
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# Supabase (HOT buffer)
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_KEY=${SUPABASE_KEY}

# Qdrant (NAS - via VPN)
QDRANT_HOST=192.168.1.129:6333

# Notion API
NOTION_API_KEY=${NOTION_API_KEY}

# Linear API
LINEAR_API_KEY=${LINEAR_API_KEY}

# Todoist API
TODOIST_API_TOKEN=${TODOIST_API_TOKEN}

# Gmail OAuth
GMAIL_CLIENT_ID=${GMAIL_CLIENT_ID}
GMAIL_CLIENT_SECRET=${GMAIL_CLIENT_SECRET}
GMAIL_REFRESH_TOKEN=${GMAIL_REFRESH_TOKEN}

# GCP Project
GCP_PROJECT_ID=premium-gastro
GCP_REGION=us-central1

# Lucy Mode
LUCY_MODE=orchestrator
LUCY_ENV=production
EOF

echo "✅ Created .env file"
echo ""

# Verify credentials
echo "🔍 Verifying credentials..."
echo ""

check_cred() {
    local name=$1
    local value=$2
    
    if [ -n "$value" ] && [ "$value" != "" ]; then
        echo "  ✅ $name"
    else
        echo "  ⚠️  $name - NOT FOUND (check 1Password item name/field)"
    fi
}

check_cred "Anthropic API Key" "$ANTHROPIC_API_KEY"
check_cred "Supabase URL" "$SUPABASE_URL"
check_cred "Supabase Key" "$SUPABASE_KEY"
check_cred "Notion API Key" "$NOTION_API_KEY"
check_cred "Linear API Key" "$LINEAR_API_KEY"
check_cred "Todoist Token" "$TODOIST_API_TOKEN"
check_cred "Gmail Client ID" "$GMAIL_CLIENT_ID"
check_cred "Gmail Client Secret" "$GMAIL_CLIENT_SECRET"
check_cred "Gmail Refresh Token" "$GMAIL_REFRESH_TOKEN"

echo ""
echo "═══════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "═══════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Review .env file if needed"
echo "  2. Run: ./deployment/deploy-local.sh (local test)"
echo "  3. Or run: ./deployment/deploy-full-gcp.sh (GCP deploy)"
echo ""
