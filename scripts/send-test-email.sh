#!/bin/bash

# Tech Trending Daily - Local Email Test Script
# Usage: ./scripts/send-test-email.sh <gmail_username> <gmail_app_password> <recipient_email>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <gmail_username> <gmail_app_password> <recipient_email>"
    echo ""
    echo "Example:"
    echo "  $0 your.email@gmail.com your-app-password recipient@example.com"
    echo ""
    echo "Note: You need to use Gmail App Password, not your regular password."
    echo "      Generate one at: https://myaccount.google.com/apppasswords"
    exit 1
fi

GMAIL_USERNAME="$1"
GMAIL_PASSWORD="$2"
RECIPIENT="$3"
SUBJECT="🔥 Tech Trending Daily - Test $(date '+%Y-%m-%d')"

echo "🚀 Tech Trending Daily - Local Test"
echo "===================================="
echo ""

# Check if test data exists
DATA_FILE="$PROJECT_DIR/test-output/trending-data-base64.txt"

if [ ! -f "$DATA_FILE" ]; then
    echo "📊 No test data found. Fetching fresh data..."
    echo ""
    
    cd "$PROJECT_DIR"
    npx ts-node scripts/test-local.ts
    echo ""
fi

if [ ! -f "$DATA_FILE" ]; then
    echo "❌ Failed to generate test data"
    exit 1
fi

echo "📧 Sending test email..."
echo "   From: $GMAIL_USERNAME"
echo "   To: $RECIPIENT"
echo "   Subject: $SUBJECT"
echo ""

# Install yagmail if needed
pip install -q yagmail

# Send email
BASE64_DATA=$(cat "$DATA_FILE")
python "$PROJECT_DIR/.github/actions/send_email.py" \
    "$GMAIL_USERNAME" \
    "$GMAIL_PASSWORD" \
    "$RECIPIENT" \
    "$SUBJECT" \
    "$BASE64_DATA"

echo ""
echo "✅ Done! Check your inbox at $RECIPIENT"

