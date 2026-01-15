# Daily News Agent

**Automated daily news aggregation system** that collects articles from 100+ RSS feeds and Reddit sources, generates AI-powered summaries using Claude, and delivers personalized updates via email and markdown files.

**🎉 v4 Status**: Fully tested and ready for production deployment! See [V4_DEPLOYMENT_READINESS.md](V4_DEPLOYMENT_READINESS.md)

---

## 🚀 Quick Start (GitHub Actions - Cloud Version)

This system runs automatically in GitHub Actions at **4:00 AM EST every day**. No local machine required!

### Viewing Your Daily Updates

1. **Check your email** for updates (subject: `Update: Day MM-DD-YY at time`)
2. **Pull latest updates to Obsidian:**
   ```bash
   cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent"
   git pull
   ```
3. Updates appear in: `Published Updates/YYYY-MM-DD-daily-update.md`

### Manual Trigger (Testing)

1. Go to: https://github.com/jonsims/daily-news-agent/actions
2. Click **"Daily News Update"** → **"Run workflow"** → **"Run workflow"**
3. Wait 2-3 minutes for completion

---

## 📊 System Status

### Cloud System (Primary)
- **Platform**: GitHub Actions
- **Schedule**: Daily at 4:00 AM EST (9:00 AM UTC)
- **Current Version**: v2 (stable) - **v4 ready to deploy**
- **Email Label**: `Update: ...` (no "Local")
- **Cost**: $0/month (free tier)
- **Output**: Commits to `Published Updates/` folder

### v4 Enhancement (Ready for Deployment)
- **Status**: ✅ Fully tested and ready
- **New Features**: Meta-summary, 4 new categories, Readwise integration, Feed Manager web UI
- **Deployment**: Change 1 line in `.github/workflows/daily-update.yml` (see [V4_DEPLOYMENT_READINESS.md](V4_DEPLOYMENT_READINESS.md))

### Local System (Backup)
- **Platform**: macOS LaunchAgent
- **Schedule**: Daily at 4:00 AM EST
- **Email Label**: `Update (Local): ...`
- **Status**: Active (can be disabled after confirming cloud works)

---

## 🔧 Configuration

### GitHub Secrets (Required for Cloud)

Set these at: https://github.com/jonsims/daily-news-agent/settings/secrets/actions

| Secret Name | Description |
|-------------|-------------|
| `CLAUDE_API_KEY` | Anthropic Claude API key (primary summarizer) |
| `OPENAI_API_KEY` | OpenAI API key (fallback summarizer) |
| `GMAIL_APP_PASSWORD` | Gmail app-specific password for email delivery |
| `GMAIL_ADDRESS` | Email address to send updates to |
| `READWISE_API_KEY` | (Optional, v4 only) Readwise API key for highlights/reader integration |

### Local Configuration

Environment variables stored in `.env` file (not committed to git):

```bash
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GMAIL_APP_PASSWORD=...
GMAIL_ADDRESS=jon.sims@gmail.com
```

---

## 📁 Project Structure

```
daily-news-agent/
├── .github/workflows/
│   └── daily-update.yml          # GitHub Actions workflow
├── config/
│   ├── sources-v2.yaml           # 77+ RSS feeds and Reddit sources
│   └── templates/
│       └── daily-update-v2.md    # Markdown template
├── src/
│   ├── main_v2.py                # Main orchestrator
│   ├── collectors/               # RSS, Reddit, Weather, APIs
│   ├── processors/               # AI summarization
│   ├── generators/               # Markdown generation
│   └── utils/                    # Email, caching, deduplication
├── Published Updates/            # Generated daily updates (git-tracked)
├── cache/                        # Temporary caches (git-ignored)
├── .env                          # API keys (git-ignored)
└── requirements.txt              # Python dependencies
```

---

## 🎯 Features

### Content Collection
- **77+ RSS Feeds**: Tech news, AI, academia, space, markets
- **Reddit Integration**: 7 subreddits for AI coding tools
- **Weather**: Daily forecast for Framingham, MA (01701)
- **Historical**: "On This Day" events
- **Daily Stoicism**: Philosophical quote extraction

### AI Summarization
- **Primary**: Claude Sonnet 4 (Anthropic)
- **Fallback**: GPT-4 (OpenAI)
- **Smart Caching**: 24-hour API response cache
- **Word Targets**: Customized by category (200-600 words)

### Content Categories (v2 - Current)
1. **Weather** (Framingham, MA)
2. **AI & Technology** (600 words) - Merged AI + tech headlines
3. **Academia & Research** (400 words)
4. **Moonshot Strategy** (300 words)
5. **Business & Markets** (300 words)
6. **US News Brief** (200 words)
7. **Space & Exploration** (200 words)
8. **Longform Reading** (200 words)
9. **Agentic Coding** (400 words) - AI coding tools
10. **Reddit Highlights** (200 words)
11. **Daily Stoicism** (50 words)

### New Categories in v4
12. **Meta-Summary** - AI-generated daily synthesis across all categories (top of email)
13. **Good News & Inspiration** (300 words)
14. **Personal Finance & FIRE** (400 words)
15. **Sustainable Homes** (300 words)
16. **Solopreneur & Startups** (300 words)
17. **Readwise Highlights** (150 words) - Personal reading highlights
18. **Readwise Reader** (200 words) - Saved articles

### Deduplication
- **24-hour cache** prevents duplicate articles
- Content filtering removes unwanted topics
- Smart article matching across sources

---

## 🌐 Web UI (October 2025 Update)

### Live Dashboard: https://daily-news-agent.pages.dev/

**Feed Manager** (Unified Interface)
- Sidebar navigation with all feed categories
- Dashboard view showing feed health statistics
- Per-category management with search/filter
- Feed suggestions with 💡 lightbulb indicator
- Toggle switches for enabling/disabling feeds
- Bulk actions (Enable All, Disable All, Disable Empty, Disable Errors)

**Email Archive** (Redesigned)
- Browse all past daily emails in web format
- Sidebar navigation with dates grouped by month
- Version filter (v2 / v4)
- Inline email viewing

**Design**
- Consistent teal/green color scheme across all pages
- Sidebar-based layout for easy navigation
- Responsive and mobile-friendly
- Auto-deploys from v4-development branch to Cloudflare Pages

See [config/web-ui/NAVIGATION.md](config/web-ui/NAVIGATION.md) for complete navigation map.

---

## 🛠️ Local Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Test mode (adds "Test" to title, doesn't affect production)
python3 src/main_v2.py --test

# Production mode (sends email, saves to Published Updates)
python3 src/main_v2.py

# Test all components
python3 src/main_v2.py --test-components
```

### Common Commands

```bash
# Pull latest updates from GitHub
git pull

# Check repository status
git status

# View recent commits
git log --oneline -10

# Clear caches (force fresh data)
rm cache/seen_articles/seen_articles.json
rm cache/api/*.cache
```

---

## 📧 Email Configuration

### Two Email Types

- **Cloud**: `Update: Day MM-DD-YY at time` (from GitHub Actions)
- **Local**: `Update (Local): Day MM-DD-YY at time` (from Mac)

Both emails are sent to the address configured in `GMAIL_ADDRESS`.

### Gmail Setup

1. Enable 2-factor authentication: https://myaccount.google.com/security
2. Generate app password: https://myaccount.google.com/apppasswords
3. Add to `.env` and GitHub Secrets

---

## 🔄 Version Control

### Sync Workflow

1. **GitHub Actions** generates update at 4 AM EST
2. Update committed to `Published Updates/` folder
3. **You pull** changes locally with `git pull`
4. Files appear in Obsidian vault automatically

### Manual Sync Alias

Add to `~/.zshrc`:
```bash
alias pull-news="cd \"/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent\" && git pull"
```

Then just run: `pull-news`

---

## 💰 Cost Analysis

### Current Costs
- **GitHub Actions**: $0/month (60 min/month used of 2,000 free)
- **Claude API**: ~$0.12/day = ~$3.60/month
- **OpenAI API**: ~$0.03/day = ~$0.90/month (fallback, rarely used)
- **Total**: ~$4.50/month

### Free Tier Usage
- **GitHub Actions**: 2,000 minutes/month free
- **Daily usage**: ~2 minutes/day = ~60 minutes/month
- **Headroom**: 97% free tier remaining

---

## 🐛 Troubleshooting

### GitHub Actions Fails

1. Go to: https://github.com/jonsims/daily-news-agent/actions
2. Click failed run → Click step to see logs
3. Common fixes:
   - Verify all 4 GitHub Secrets are set correctly
   - Check API keys are valid
   - Ensure Gmail App Password is correct

### No Email Received

- Check spam/junk folder
- Search for: `from:jon.sims@gmail.com subject:Update`
- Verify `GMAIL_ADDRESS` secret matches your email
- Check workflow logs for email sending confirmation

### Local Version Still Running

```bash
# Disable local LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.jonsims.dailynews.plist

# Re-enable if needed
launchctl load ~/Library/LaunchAgents/com.jonsims.dailynews.plist
```

---

## 📚 Documentation

- **[V4_DEPLOYMENT_READINESS.md](V4_DEPLOYMENT_READINESS.md)**: v4 testing results and deployment instructions (NEW)
- **[CLAUDE.md](CLAUDE.md)**: Claude Code project context (updated for v4)
- **[config/web-ui/NAVIGATION.md](config/web-ui/NAVIGATION.md)**: Web UI navigation map (NEW)
- **[GITHUB_MIGRATION_PLAN.md](GITHUB_MIGRATION_PLAN.md)**: Complete migration guide
- **[CHANGELOG.md](CHANGELOG.md)**: Version history
- **[AUTOMATION_SETUP.md](AUTOMATION_SETUP.md)**: Original local automation setup
- **[API_OPTIMIZATION.md](API_OPTIMIZATION.md)**: Performance optimization notes

---

## 🔐 Security

### Protected Files (.gitignore)

- `.env` - API keys and credentials
- `cache/` - Temporary data
- `*.log` - Log files
- `__pycache__/` - Python bytecode

### GitHub Secrets

All sensitive credentials stored as encrypted GitHub Secrets, never committed to repository.

---

## 📈 Version

**Current Production**: v2 (v0.3)
**Ready to Deploy**: v4 (v0.4) - See [V4_DEPLOYMENT_READINESS.md](V4_DEPLOYMENT_READINESS.md)

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your own use!

### v4 Features
- Meta-summary generation with theme tracking
- 4 new content categories
- Readwise integration (highlights + reader)
- Enhanced web UI with Feed Manager
- Improved AI summarization
- Feed status monitoring

### Adding RSS Feeds

Edit `config/sources-v2.yaml`:

```yaml
categories:
  your_category:
    sources:
      - url: "https://example.com/feed.xml"
        name: "Source Name"
```

### Adding Categories

1. Update `config/sources-v2.yaml`
2. Update `src/main_v2.py` (consolidation + word targets)
3. Update `config/templates/daily-update-v2.md`
4. Update `src/generators/markdown_v2.py`

---

## 📞 Support

For issues or questions about the Daily News Agent system, refer to the documentation files or GitHub Actions logs.

---

**Last Updated**: October 11, 2025
**Migration Completed**: October 1, 2025
**v4 Testing Completed**: October 11, 2025
**System Status**: ✅ Operational (v2 in production, v4 ready to deploy)
