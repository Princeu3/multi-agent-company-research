# 🚀 GitHub Setup Instructions

## Step 1: Create Repository on GitHub

1. Go to [GitHub](https://github.com/new)
2. Repository name: `multi-agent-company-research` (or your preferred name)
3. Description: `Multi Agent Company Research System - AI-powered multi-agent platform for researching and analyzing company ESG sustainability practices`
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

## Step 2: Push to GitHub

After creating the repository, run one of these commands:

### Option A: Using the provided script
```bash
./push_to_github.sh Princeu3 multi-agent-company-research
```

### Option B: Manual commands
```bash
# Add remote (replace with your actual username/repo if different)
git remote add origin git@github.com:Princeu3/multi-agent-company-research.git

# Or if using HTTPS:
# git remote add origin https://github.com/Princeu3/multi-agent-company-research.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify

Visit your repository at:
`https://github.com/Princeu3/multi-agent-company-research`

---

**Note:** If you get authentication errors, make sure:
- You have SSH keys set up with GitHub (for SSH URLs)
- Or use HTTPS and authenticate when prompted
- Or use a Personal Access Token for HTTPS

