#!/bin/bash
# Hugging Face Spaces Deployment Script
# Usage: ./deploy-hf.sh YOUR_HF_TOKEN

set -e

HF_TOKEN=$1
SPACE_NAME="neelumghazal/lumina-todo-api"

if [ -z "$HF_TOKEN" ]; then
    echo "Usage: ./deploy-hf.sh YOUR_HF_TOKEN"
    echo ""
    echo "Get your token from: https://huggingface.co/settings/tokens"
    exit 1
fi

echo "🚀 Deploying to Hugging Face Space: $SPACE_NAME"

# Create temp directory
TEMP_DIR=$(mktemp -d)
echo "📁 Working in: $TEMP_DIR"

# Copy backend files
cp Dockerfile "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp README.md "$TEMP_DIR/"
cp -r app "$TEMP_DIR/"

# Upload to HF Space
echo "📤 Uploading files..."
cd "$TEMP_DIR"
huggingface-cli upload "$SPACE_NAME" . . \
    --repo-type space \
    --token "$HF_TOKEN" \
    --commit-message "Deploy Lumina Todo API backend"

echo ""
echo "✅ Deployment initiated!"
echo "🔗 Space URL: https://huggingface.co/spaces/$SPACE_NAME"
echo "🌐 API URL: https://neelumghazal-lumina-todo-api.hf.space"
echo ""
echo "⏳ Wait 8-10 minutes for Docker build to complete."
echo "🔍 Check build logs at: https://huggingface.co/spaces/$SPACE_NAME/logs"

# Cleanup
rm -rf "$TEMP_DIR"
