#!/bin/bash

# Script to push Multi Agent Company Research System to GitHub
# Usage: ./push_to_github.sh <your-github-username> <repo-name>

GITHUB_USERNAME=${1:-Princeu3}
REPO_NAME=${2:-multi-agent-company-research}

echo "🚀 Pushing to GitHub repository: $GITHUB_USERNAME/$REPO_NAME"

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "⚠️  Remote 'origin' already exists. Updating..."
    git remote set-url origin git@github.com:$GITHUB_USERNAME/$REPO_NAME.git
else
    echo "➕ Adding remote 'origin'..."
    git remote add origin git@github.com:$GITHUB_USERNAME/$REPO_NAME.git
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🌐 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

