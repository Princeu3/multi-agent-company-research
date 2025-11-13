# 🚀 Streamlit Cloud Deployment Guide

## Summary: Will It Work?

**YES!** Your app is ready for Streamlit Cloud with some important considerations:

✅ **What Works:**
- All Python dependencies are compatible
- Streamlit app structure is perfect
- PDF generation will work
- Chat interface will work
- Download functionality will work

⚠️ **What to Know:**
- SQLite database **will NOT persist** between deployments (data resets on restart)
- You need to configure 3 API keys in Streamlit Cloud secrets
- First load might be slow (~30 seconds)

---

## 📋 Pre-Deployment Checklist

### ✅ 1. GitHub Repository Setup

```bash
# Make sure code is in GitHub
git status
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### ✅ 2. Verify .gitignore

Ensure these are in `.gitignore`:

```gitignore
.env
.streamlit/secrets.toml
*.db
__pycache__/
*.pyc
.DS_Store
```

### ✅ 3. Prepare API Keys

You need these 3 API keys ready:

1. **OpenAI API Key** - Get from: https://platform.openai.com/api-keys
2. **Perplexity API Key** - Get from: https://www.perplexity.ai/settings/api
3. **Firecrawl API Key** - Get from: https://www.firecrawl.dev/

---

## 🚀 Deployment Steps

### Step 1: Go to Streamlit Cloud

1. Visit: https://share.streamlit.io
2. Sign in with your GitHub account
3. Grant Streamlit access to your repositories

### Step 2: Create New App

1. Click **"Create app"** (upper-right corner)
2. When asked "Do you already have an app?" click **"Yup, I have an app"**

### Step 3: Configure App Settings

Fill in the deployment form:

```
Repository: your-github-username/DSDA
Branch: main
Main file path: app.py
App URL: choose-your-subdomain (e.g., "esg-analyzer")
```

### Step 4: Advanced Settings (CRITICAL!)

1. Click **"Advanced settings"**
2. **Python version:** Select `3.9` (or 3.10, 3.11)
3. **Secrets:** Paste this (with your actual keys):

```toml
# Required API Keys
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxx"
PERPLEXITY_API_KEY = "pplx-xxxxxxxxxxxxxxxxxxxxx"
FIRECRAWL_API_KEY = "fc-xxxxxxxxxxxxxxxxxxxxx"

# Optional Configuration
CACHE_EXPIRY_DAYS = "7"
LOG_LEVEL = "INFO"
```

4. Click **"Save"**

### Step 5: Deploy!

1. Click **"Deploy"** button
2. Wait 2-5 minutes for build to complete
3. Watch build logs for any errors
4. Once deployed, you'll get a URL like: `https://your-app.streamlit.app`

---

## 🧪 Testing After Deployment

### 1. Test Basic Functionality

```
✅ App loads successfully
✅ Chat interface appears
✅ Sidebar shows correctly
✅ "Analyze Tesla" works
✅ Company appears in sidebar
✅ "Download Tesla report" works
✅ PDF downloads successfully
```

### 2. Test API Connections

If you see errors like:
- "API key not found" → Check secrets configuration
- "Module not found" → Check requirements.txt
- "Database error" → This is normal on first load, database initializes automatically

---

## ⚠️ Known Limitations on Streamlit Cloud

### 1. Database Persistence

**Problem:** SQLite data resets when app restarts or redeploys

**Impact:**
- Users lose analyzed company data
- App works as a "per-session" analysis tool
- Good for demos, not for production data storage

**Solutions:**
- **Short-term:** Accept as demo tool, encourage PDF downloads
- **Long-term:** Migrate to cloud database (PostgreSQL, MongoDB Atlas)

### 2. API Rate Limits

**Problem:** Multiple users share your API keys

**Impact:**
- Could hit OpenAI/Perplexity/Firecrawl rate limits
- Costs increase with usage

**Solutions:**
- Monitor API usage in respective dashboards
- Consider adding user authentication
- Set up usage quotas if needed

### 3. Cold Starts

**Problem:** App sleeps after inactivity, slow first load

**Impact:**
- First user after idle period waits ~30 seconds
- Subsequent loads are fast

**Solutions:**
- This is normal for free Streamlit Cloud
- Upgrade to paid plan for always-on apps

---

## 🐛 Common Deployment Issues & Fixes

### Issue 1: "ModuleNotFoundError"

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Fix:**
```bash
# Ensure all dependencies in requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Issue 2: "API Key Not Found"

**Error:** `OpenAI API key not found` or similar

**Fix:**
1. Go to app settings in Streamlit Cloud
2. Click "Secrets" tab
3. Verify keys are pasted correctly (no extra spaces)
4. Reboot app

### Issue 3: "Database Locked"

**Error:** `sqlite3.OperationalError: database is locked`

**Fix:**
- This can happen with concurrent users
- Consider upgrading to PostgreSQL for production
- Or add a warning: "Single-user demo - avoid concurrent use"

### Issue 4: App Crashes on Startup

**Fix:**
1. Check logs in Streamlit Cloud dashboard
2. Look for import errors or missing dependencies
3. Verify all file paths use `/` not `\`
4. Ensure no hardcoded absolute paths

---

## 📊 Monitoring Your Deployed App

### Streamlit Cloud Dashboard

Access at: https://share.streamlit.io

**Monitor:**
- App status (running, sleeping, error)
- Logs (real-time error messages)
- Resource usage (CPU, memory)
- Analytics (views, unique visitors)

### API Usage

**OpenAI:**
- Dashboard: https://platform.openai.com/usage
- Set spending limits
- Monitor costs

**Perplexity:**
- Check your account dashboard
- Track query counts

**Firecrawl:**
- Monitor scraping credits
- Check rate limits

---

## 🔒 Security Best Practices

### 1. Never Commit Secrets

```bash
# Always check before pushing
git status
git diff

# If you accidentally committed secrets:
git rm --cached .env
git commit -m "Remove secrets"
git push --force  # Use with caution!
```

### 2. Rotate API Keys Regularly

- Change keys every 3-6 months
- Update in Streamlit Cloud secrets
- Reboot app after updating

### 3. Monitor for Abuse

- Watch for unusual API usage spikes
- Consider adding authentication
- Use Streamlit's built-in analytics

---

## 💰 Cost Considerations

### Free Tier Limits

**Streamlit Cloud (Free):**
- ✅ 1 private app
- ✅ Unlimited public apps
- ✅ Community support
- ⚠️ App sleeps after inactivity
- ⚠️ 1 GB RAM limit

**API Costs (Estimated for moderate use):**
- OpenAI GPT-4o-mini: ~$0.15 per 1M tokens (input) / $0.60 per 1M tokens (output)
- Perplexity: Check pricing at perplexity.ai
- Firecrawl: Check pricing at firecrawl.dev

**Per Company Analysis (Rough Estimate):**
- ~10 Perplexity queries
- ~5 Firecrawl scrapes
- ~50,000 tokens to OpenAI
- **Total: ~$0.05-0.15 per analysis**

---

## 🔄 Updating Your Deployed App

### Auto-Deploy (Recommended)

Every `git push` to main branch triggers automatic redeployment:

```bash
git add .
git commit -m "Add new feature"
git push origin main
# App automatically redeploys in 2-3 minutes
```

### Manual Reboot

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "⋮" menu → "Reboot app"

### Revert to Previous Version

```bash
git log  # Find commit hash
git revert <commit-hash>
git push
```

---

## 📈 Upgrading for Production

If you need to handle more users or persist data:

### Option 1: Migrate Database

**PostgreSQL (Recommended):**
- Use Supabase (free tier available)
- Or Railway, Heroku, AWS RDS
- Update `database/db_manager.py` to use PostgreSQL

**MongoDB:**
- Use MongoDB Atlas (free tier)
- Refactor database layer

### Option 2: Add Authentication

- Use `streamlit-authenticator` package
- Limit access to authorized users
- Track per-user API usage

### Option 3: Upgrade Streamlit Cloud

**Streamlit Community Cloud ($20/month):**
- No sleeping apps
- More resources (2 GB RAM)
- Priority support

---

## ✅ Final Checklist Before Going Live

- [ ] All 3 API keys configured in secrets
- [ ] `.gitignore` includes `.env` and `secrets.toml`
- [ ] App tested locally with `streamlit run app.py`
- [ ] Git repository pushed to GitHub
- [ ] App deployed to Streamlit Cloud
- [ ] Basic functionality tested on live URL
- [ ] PDF download tested on live URL
- [ ] Share URL with intended users
- [ ] Monitor logs for first 24 hours
- [ ] Check API usage after first week

---

## 🆘 Getting Help

If you encounter issues:

1. **Streamlit Docs:** https://docs.streamlit.io/deploy/streamlit-community-cloud
2. **Streamlit Forum:** https://discuss.streamlit.io
3. **GitHub Issues:** Check your app's repo issues
4. **Logs:** Always check Streamlit Cloud logs first

---

## 🎉 Success!

Once deployed, your app will be accessible at:
```
https://your-chosen-subdomain.streamlit.app
```

Share this URL with users to start analyzing company sustainability! 🌱
