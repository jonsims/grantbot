# GitHub Migration Plan - Daily News Agent

## Overview

This document outlines the complete plan to migrate the Daily News Agent from local macOS automation (LaunchAgent) to cloud-based automation using GitHub Actions. This will enable the daily update to run automatically at 4:00 AM EST every day, regardless of whether your local machine is powered on.

**Current Status:** Running locally via macOS LaunchAgent
**Target Status:** Running in GitHub Actions cloud
**Migration Difficulty:** Easy (3/10)
**Estimated Time:** 30-45 minutes
**Additional Cost:** $0 (GitHub Actions free tier covers usage)

---

## Why Migrate to GitHub Actions?

### Current Limitations (Local Execution)
- ❌ Requires Mac to be powered on at 4:00 AM
- ❌ No execution if Mac is asleep, off, or disconnected
- ❌ No backup/redundancy if Mac has issues
- ❌ Can't run when traveling without laptop

### Benefits of GitHub Actions
- ✅ Runs 24/7 in the cloud, independent of your machine
- ✅ Free tier: 2,000-3,000 minutes/month (only need ~60 minutes/month)
- ✅ Reliable scheduled execution
- ✅ Built-in logging and monitoring
- ✅ Version control for all generated updates
- ✅ Can run from anywhere (just check email or GitHub)

---

## System Architecture Analysis

### Current Local Setup
```
MacOS LaunchAgent (4:00 AM)
    ↓
run_daily_update.sh
    ↓
main_v2.py (Python script)
    ↓
    ├─ Collect RSS feeds (77 sources)
    ├─ Call Claude API for summaries
    ├─ Generate markdown file
    ├─ Save to: Published Updates/YYYY-MM-DD-daily-update.md
    └─ Send email via Gmail SMTP
```

### Target GitHub Actions Setup
```
GitHub Actions (4:00 AM EST)
    ↓
Workflow: daily-update.yml
    ↓
main_v2.py (Python script)
    ↓
    ├─ Collect RSS feeds (77 sources)
    ├─ Call Claude API for summaries
    ├─ Generate markdown file
    ├─ Commit to repo: Published Updates/YYYY-MM-DD-daily-update.md
    └─ Send email via Gmail SMTP
```

---

## File Delivery Options

You must choose how to get the generated markdown files into your Obsidian vault:

### Option A: Git Commit to Repository ⭐ **RECOMMENDED**

**How it works:**
1. GitHub Actions generates the daily update
2. Commits the file to `Published Updates/` folder in the repo
3. You sync to Obsidian using one of:
   - **Obsidian Git Plugin** (automatic pull on startup)
   - Manual `git pull` when you want to see updates
   - GitHub Desktop app

**Pros:**
- ✅ Complete version history of all updates
- ✅ Can easily revert or view old versions
- ✅ Everything in one centralized location
- ✅ Obsidian Git plugin makes it seamless
- ✅ No additional services/APIs needed

**Cons:**
- ⚠️ Requires installing Obsidian Git plugin OR manual sync
- ⚠️ Adds git commits to your repo history daily

**Best for:** Users who want full automation and version control

---

### Option B: Email Only (Simplest)

**How it works:**
1. GitHub Actions generates the daily update
2. Sends email (as it does now)
3. You manually copy/paste into Obsidian if desired

**Pros:**
- ✅ Simplest setup - no sync required
- ✅ Minimal changes to current workflow

**Cons:**
- ❌ No automatic Obsidian integration
- ❌ Manual work to add to vault
- ❌ No version history in repo

**Best for:** Users who primarily consume via email

---

### Option C: Cloud Storage Sync (Advanced)

**How it works:**
1. GitHub Actions generates the daily update
2. Uploads to Dropbox/Google Drive via API
3. Obsidian vault syncs via cloud service

**Pros:**
- ✅ True automation - no manual steps
- ✅ Works with existing cloud sync setup

**Cons:**
- ❌ Requires additional API setup (Dropbox/Google Drive)
- ❌ More complex configuration
- ❌ Additional credentials to manage

**Best for:** Advanced users with existing cloud workflows

---

## Prerequisites

### What You Already Have ✅
- Python 3.9+ installed
- Working `daily-news-agent` system
- API keys in `.env` file:
  - `CLAUDE_API_KEY`
  - `OPENAI_API_KEY`
  - `GMAIL_APP_PASSWORD`
  - `GMAIL_ADDRESS`
- All dependencies in `requirements.txt`

### What You Need to Set Up
1. GitHub account (free)
2. Git installed on your Mac (already installed on macOS)
3. Choose file delivery option (recommend Option A)
4. *Optional:* Obsidian Git plugin (if using Option A)

---

## Step-by-Step Migration Guide

### Phase 1: Prepare Repository

#### Step 1.1: Create .gitignore File

**Why:** Prevent committing sensitive data (API keys, cache)

Create `.gitignore` in `/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent/`:

```
# Secrets and environment
.env
*.env

# Cache files
cache/
*.cache

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/

# Logs
logs/
*.log

# macOS
.DS_Store
.AppleDouble
.LSOverride

# IDE
.vscode/
.idea/
*.swp
*.swo
```

#### Step 1.2: Initialize Git Repository

```bash
cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent"
git init
git add .
git commit -m "Initial commit: Daily News Agent v0.3"
```

---

### Phase 2: Create GitHub Repository

#### Step 2.1: Create New Repository

1. Go to https://github.com/new
2. **Repository name:** `daily-news-agent` (or your choice)
3. **Privacy:** ⚠️ **PRIVATE** (recommended - protects workflow/configuration)
4. **Do NOT check:** "Initialize with README" (you already have code)
5. Click "Create repository"

#### Step 2.2: Push Local Repository to GitHub

GitHub will show you commands like this:

```bash
cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent"
git remote add origin https://github.com/YOUR_USERNAME/daily-news-agent.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

### Phase 3: Configure GitHub Secrets

GitHub Secrets store your API keys securely. The workflow file will reference these.

#### Step 3.1: Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these 4 secrets (get values from your `.env` file):

| Secret Name | Value Location | Example Format |
|-------------|---------------|----------------|
| `CLAUDE_API_KEY` | From `.env` | `sk-ant-api03-...` |
| `OPENAI_API_KEY` | From `.env` | `sk-proj-...` |
| `GMAIL_APP_PASSWORD` | From `.env` | `abcd efgh ijkl mnop` |
| `GMAIL_ADDRESS` | From `.env` | `jon.sims@gmail.com` |

⚠️ **Important:**
- Never commit `.env` to GitHub
- Double-check `.gitignore` includes `.env`
- Secrets are encrypted and hidden in GitHub

---

### Phase 4: Create GitHub Actions Workflow

#### Step 4.1: Create Workflow Directory

```bash
mkdir -p "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent/.github/workflows"
```

#### Step 4.2: Create Workflow File

Create `.github/workflows/daily-update.yml`:

```yaml
name: Daily News Update

on:
  schedule:
    # Run at 4:00 AM EST (9:00 AM UTC) every day
    - cron: '0 9 * * *'
  workflow_dispatch:  # Allow manual trigger for testing

jobs:
  generate-update:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run daily update
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          GMAIL_ADDRESS: ${{ secrets.GMAIL_ADDRESS }}
        run: |
          python src/main_v2.py --output "Published Updates"

      - name: Commit and push changes
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add "Published Updates/*.md"
          git diff --staged --quiet || git commit -m "Daily update: $(date +'%Y-%m-%d')"
          git push
```

**Workflow Explanation:**
- **Trigger:** Runs daily at 9:00 AM UTC (4:00 AM EST)
- **Manual trigger:** Can test via "Actions" tab in GitHub
- **Python 3.9:** Matches your local environment
- **Secrets:** Injected as environment variables
- **Commit:** Automatically commits generated file to repo

#### Step 4.3: Adjust for Timezone (if needed)

The cron schedule `0 9 * * *` runs at 9:00 AM UTC, which is:
- **4:00 AM EST** (Eastern Standard Time, winter)
- **5:00 AM EDT** (Eastern Daylight Time, summer)

If you want consistent 4:00 AM local time year-round, you may need to manually adjust the cron during DST changes, or accept the 1-hour shift.

---

### Phase 5: Test the Workflow

#### Step 5.1: Commit and Push Workflow File

```bash
cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent"
git add .github/workflows/daily-update.yml
git commit -m "Add GitHub Actions workflow for daily updates"
git push
```

#### Step 5.2: Manual Test Run

1. Go to your GitHub repo
2. Click **Actions** tab
3. Click **Daily News Update** workflow
4. Click **Run workflow** → **Run workflow** (green button)
5. Wait 2-3 minutes for completion
6. Check:
   - ✅ Workflow shows green checkmark
   - ✅ New file in `Published Updates/` folder
   - ✅ Email received at your Gmail

#### Step 5.3: Verify Scheduled Run

- Wait until the next scheduled time (4:00 AM EST)
- Check GitHub Actions tab for automatic run
- Verify email and file creation

---

### Phase 6: Set Up Obsidian Sync (Option A)

If you chose **Option A: Git Commit**, you need to sync updates to Obsidian:

#### Option A1: Obsidian Git Plugin (Recommended)

1. Open Obsidian
2. Settings → Community plugins → Browse
3. Search "Obsidian Git"
4. Install and enable
5. Configure:
   - **Auto pull interval:** 10 minutes (or your preference)
   - **Auto commit:** Disable (you don't need to push from Obsidian)
   - **Pull updates on startup:** Enable

Now your vault will automatically sync when you open Obsidian!

#### Option A2: Manual Git Pull

```bash
cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)"
git pull
```

Run this whenever you want to see the latest update.

#### Option A3: GitHub Desktop

1. Download GitHub Desktop: https://desktop.github.com/
2. Clone your repository
3. App will notify you of changes
4. Click "Pull" to sync

---

## Maintenance and Monitoring

### Checking Workflow Status

1. Go to repository → **Actions** tab
2. View recent runs
3. Click on any run to see:
   - Execution logs
   - API calls
   - Errors (if any)

### Viewing Logs

- GitHub Actions logs are retained for 90 days
- Download logs if you need to debug issues

### Troubleshooting

**Workflow fails:**
- Check "Actions" tab for error messages
- Verify all 4 secrets are correctly set
- Check if API keys are still valid

**No email received:**
- Check Gmail App Password is correct
- Verify Gmail allows "Less secure app access" (if needed)
- Check spam folder

**File not in Obsidian:**
- Option A: Pull from GitHub (manually or via plugin)
- Option B: Check GitHub repo - file should be there
- Verify workflow completed successfully

---

## Cost Analysis

### Current Costs (Local)
- **Compute:** $0 (your Mac)
- **API Costs:** ~$0.15/day = ~$4.50/month
  - Claude API: ~$0.12/day
  - OpenAI (fallback): ~$0.03/day (rarely used)
- **Total:** ~$4.50/month

### After Migration (GitHub Actions)
- **Compute:** $0 (GitHub Actions free tier)
  - Free tier: 2,000-3,000 minutes/month
  - Usage: ~2 minutes/day = ~60 minutes/month
  - Well within limits!
- **API Costs:** ~$0.15/day = ~$4.50/month (unchanged)
- **Total:** ~$4.50/month

**Net Change:** $0 additional cost

---

## Rollback Plan

If you need to revert to local execution:

1. Disable GitHub Actions workflow:
   ```bash
   # Rename workflow file to disable it
   git mv .github/workflows/daily-update.yml .github/workflows/daily-update.yml.disabled
   git commit -m "Disable GitHub Actions"
   git push
   ```

2. Re-enable local LaunchAgent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.jonsims.dailynews.plist
   ```

Your local setup is still intact and can run immediately.

---

## Future Enhancements

Once migrated, you can easily add:

### Notifications
- GitHub Actions can send notifications to Slack, Discord, etc.
- Add a step to post summary to communication tools

### Multiple Schedules
- Add afternoon briefing (e.g., 3 PM)
- Weekend edition with different sources

### A/B Testing
- Run different configurations in parallel
- Compare AI models (Claude vs OpenAI vs local)

### Archive Management
- Auto-compress old updates
- Generate monthly summaries

---

## Quick Reference Commands

### Local Development
```bash
# Test locally before pushing
cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent"
python3 src/main_v2.py --test

# Check git status
git status

# Push changes to GitHub
git add .
git commit -m "Description of changes"
git push
```

### GitHub Actions
```bash
# View recent workflow runs (via gh CLI)
gh run list --workflow=daily-update.yml

# View logs for latest run
gh run view --log

# Trigger manual workflow run
gh workflow run daily-update.yml
```

---

## Decision Summary

**Recommended Configuration:**
- ✅ Private GitHub repository
- ✅ Option A: Git commit with Obsidian Git plugin
- ✅ Daily schedule: 4:00 AM EST (9:00 AM UTC)
- ✅ Email notifications: Enabled

**Why this works best:**
- Full automation - no manual steps
- Complete version history
- Zero additional cost
- Easy to monitor and debug
- Seamless Obsidian integration

---

## Next Steps

When ready to implement:

1. Review this entire document
2. Decide on file delivery option (A, B, or C)
3. Follow Phase 1-6 step-by-step
4. Test thoroughly before disabling local LaunchAgent
5. Monitor for 1 week to ensure stability

**Estimated Time:** 30-45 minutes for full setup

---

## Questions to Answer Before Starting

- [ ] Which file delivery option do you prefer? (A, B, or C)
- [ ] Do you have a GitHub account? (free tier is fine)
- [ ] Is your Obsidian vault folder safe to convert to a git repository?
- [ ] Are you comfortable with git commands, or prefer GitHub Desktop?
- [ ] Want to keep local LaunchAgent as backup, or disable it?

---

## Support Resources

- **GitHub Actions Documentation:** https://docs.github.com/en/actions
- **Obsidian Git Plugin:** https://github.com/denolehov/obsidian-git
- **Cron Schedule Help:** https://crontab.guru/

---

*Document Created: September 30, 2025*
*System Version: v0.3*
*Author: Claude Code*