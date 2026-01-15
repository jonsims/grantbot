# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily news aggregation system that collects articles from 100+ RSS feeds and Reddit sources, generates AI-powered summaries using Claude (with OpenAI fallback), and delivers personalized daily updates via email and markdown files at 5:00 AM EST.

**Current Status**: ✅ v5 deployed and running in production on v5-development branch
- GitHub Actions: `python src/main_v5.py` daily at 5:00 AM EST
- Web UI: https://daily-news-agent.pages.dev/
- Multi-recipient email via JSON config
- v4 workflow disabled, v2 is legacy code

**Key v5 Features**: Multi-recipient email, configurable settings (tone, features), theme tracking, meta-summaries, Readwise integration

## Version Management

**YOU ARE ON v5-development (production branch)**

**Branch Strategy**:
- **v5-development**: Production - v5 files (`main_v5.py`, `sources-v5.yaml`) - **ACTIVE**
- **v4-development**: Legacy - v4 files (workflow disabled)
- **main**: Legacy - v2 files (deprecated)

**Workflows**:
- Production: `.github/workflows/daily-update-v5.yml` ✅ Active
- Legacy: `.github/workflows/daily-update.yml` ⚙️ Disabled

See [V5_DEVELOPMENT.md](V5_DEVELOPMENT.md) for v5 testing guide and [V4_DEPLOYMENT_READINESS.md](V4_DEPLOYMENT_READINESS.md) for history.

### Essential Commands

**Production (v5)** - You are on v5-development branch:
```bash
# Test mode (adds "Test" to title, deduplication disabled, sends email)
python3 src/main_v5.py --test

# Production mode (sends to all recipients, saves to Published Updates/)
python3 src/main_v5.py

# Test all components (collectors, AI, email)
python3 src/main_v5.py --test-components
```

**Legacy versions** (v4: `python3 src/main_v4.py`, v2: `python3 src/main_v2.py`) - Reference only

**Utility commands**:
```bash
# Clear deduplication cache (24-hour window)
rm cache/seen_articles/seen_articles.json

# Clear API cache (forces fresh AI summaries)
rm cache/api/*.cache

# Pull latest updates from GitHub
git pull
```

## V5 Multi-Recipient Email Configuration

V5's primary feature is support for sending daily updates to multiple email recipients via JSON configuration.

### Recipients Configuration

**Configuration File**: [config/v5-recipients.json](config/v5-recipients.json)
**Web UI Manager**: https://daily-news-agent.pages.dev/config/web-ui/v5-recipients.html

**JSON Format**:
```json
{
  "recipients": [
    "email1@gmail.com",
    "email2@gmail.com"
  ],
  "updated_at": "2025-10-15T14:30:00Z",
  "version": "v5",
  "description": "Email recipients for V5 daily news updates"
}
```

**Adding Recipients**:
1. **Via Web UI**: Visit [v5-recipients.html](https://daily-news-agent.pages.dev/config/web-ui/v5-recipients.html) and use the form
2. **Via JSON**: Edit `config/v5-recipients.json` directly and commit to git
3. **Via local file**: Also supported at root `v5-recipients.json` (fallback)
4. Changes take effect on next automated run (5:00 AM EST)

**Implementation**: See [src/utils/email_sender_v5.py](src/utils/email_sender_v5.py) - Multi-recipient SMTP sending

### V5 Settings Configuration

**Configuration File**: [config/v5-settings.json](config/v5-settings.json)
**Web UI Manager**: https://daily-news-agent.pages.dev/config/web-ui/v5-settings.html

**Available Settings**:
- `meta_summary.tone`: "analytical", "conversational", or "mixed" (default)
- `features.readwise_enabled`: true/false (default: false)
- `features.stoicism_enabled`: true/false (default: false)

**JSON Format**:
```json
{
  "meta_summary": {
    "tone": "mixed",
    "description": "Tone options: analytical, conversational, mixed"
  },
  "features": {
    "readwise_enabled": false,
    "stoicism_enabled": false,
    "description": "Toggle optional features on/off"
  },
  "updated_at": "2025-10-15T21:15:00Z",
  "version": "v5"
}
```

**Changing Settings**:
1. **Via Web UI**: Visit [v5-settings.html](https://daily-news-agent.pages.dev/config/web-ui/v5-settings.html)
2. **Via JSON**: Edit `config/v5-settings.json` directly and commit
3. Changes take effect on next automated run

**Implementation**: Settings loaded in [src/main_v5.py](src/main_v5.py) via `_load_settings()` method

## System Architecture

### Data Flow Pipeline

**v5 Production Pipeline** ([main_v5.py](src/main_v5.py) - **CURRENTLY RUNNING**):
1. **Collection** → Concurrent RSS/Reddit/Readwise via `rss_collector_enhanced.py`
2. **Filtering** → Content filtering via `content_filter.py` (removes unwanted topics)
3. **Deduplication** → 24-hour cache via `deduplication.py` (disabled in test mode)
4. **Consolidation** → Merge categories (e.g., ai + tech_tools → ai_technology)
5. **AI Summarization** → Claude Sonnet 4 → GPT-4 fallback via `ai_summarizer_v5.py`
6. **Theme Tracking** → 7-day trend analysis via `theme_tracker_v5.py`
7. **Meta-Summary** → AI synthesis across categories (tone configurable via settings)
8. **Generation** → Markdown + HTML email via `markdown_v5.py`
9. **Feed Status** → Health monitoring JSON for web UI
10. **Delivery** → Multi-recipient email via `email_sender_v5.py` + commit to `Published Updates/`

**v4/v2 Legacy**: Similar pipeline but single-recipient email, no settings config (v4 disabled, v2 deprecated)


### Category Consolidation Logic

The system merges raw source categories into 13 consolidated output categories (see [main_v5.py:117-149](src/main_v5.py#L117-149)):

**Category Merges**:
- `ai` + `tech_tools` + `tech_headlines` → `ai_technology` (600 words)
- `academic_research` + `higher_education` → `academia_research` (400 words)
- `from_reddit` → `reddit_highlights` (200 words)

**Direct Pass-through Categories**:
- `moonshot_strategy` (500 words), `good_news` (300 words), `personal_finance_fire` (400 words), `sustainable_homes` (300 words), `solopreneur_startups` (300 words)
- `readwise_highlights` (150 words), `readwise_reader` (200 words) - Configurable via settings
- `market_business`, `us_news`, `space_news`, `longform_articles`, `agentic_coding`, `daily_stoicism` (configurable), `on_this_day`, `weather`

See [sources-v5.yaml](config/sources-v5.yaml) for full source list (100+ feeds).


### AI Summarization Configuration

**Models**: `claude-sonnet-4-20250514` (primary) → `gpt-4` (automatic fallback) - See [ai_summarizer_v5.py:54](src/processors/ai_summarizer_v5.py#L54)
**Cache**: 24-hour TTL in `cache/api/` via `APIResponseCache`

**Word Targets** (see [main_v5.py:223-241](src/main_v5.py#L223-241)):
- Large (400-600): ai_technology: 600 | moonshot_strategy: 500 | academia_research: 400 | agentic_coding: 400 | personal_finance_fire: 400
- Medium (300): good_news | market_business | sustainable_homes | solopreneur_startups
- Small (150-200): space_news | us_news | longform_articles | reddit_highlights | readwise_highlights: 150 | readwise_reader: 200
- Tiny (30-50): on_this_day: 50 | weather: 30 | daily_stoicism: 50

### Deduplication System

**Window**: 24 hours (changed from 7 days to increase article count)
**File**: `src/utils/deduplication.py:30`
**Logic**: Hash-based matching on URL + title
**Cache Location**: `cache/seen_articles/seen_articles.json`

**V5 Test Mode**: Deduplication is **disabled** in `--test` mode for fuller previews

To adjust deduplication window:
```python
# src/utils/deduplication.py:30
cutoff = (datetime.now() - timedelta(hours=24))  # Change hours=24 to desired value
```

## GitHub Actions Automation

**V5 Production Workflow**: `.github/workflows/daily-update-v5.yml`
**Schedule**: Daily at 5:00 AM EST (10:00 AM UTC)
**Trigger**: Cron + manual dispatch
**Status**: ✅ **ACTIVE** (primary production system)

**V4 Legacy Workflow**: `.github/workflows/daily-update.yml`
**Status**: ⚙️ **DISABLED** (no schedule, manual dispatch only)

**Required GitHub Secrets**:
- `CLAUDE_API_KEY` - Anthropic Claude API key
- `OPENAI_API_KEY` - OpenAI API key (fallback)
- `GMAIL_APP_PASSWORD` - Gmail app-specific password

**Optional GitHub Secrets** (for v5):
- `READWISE_API_KEY` - Readwise API key for highlights/reader integration (can be disabled via v5-settings.json)

**Note**: v5 recipients are managed via `config/v5-recipients.json` file (committed to repo), not via GitHub secrets. This allows web UI management without requiring secret updates.

**Environment Variables**:
- `UPDATE_SOURCE=Web` (GitHub Actions) vs `Local` (macOS LaunchAgent)
  - Used to label email subjects: "Update Agent Email v5 beta - ..." (Web) vs "Update (Local): ..." (Local)
- All API keys can be set in `.env` file for local development

**Local `.env` file format**:
```bash
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GMAIL_APP_PASSWORD=...
READWISE_API_KEY=...  # Optional, can be disabled via v5-settings.json
UPDATE_SOURCE=Local
```

**Workflow Steps**:
1. Checkout repository
2. Setup Python 3.11
3. Install dependencies from `requirements.txt`
4. Run `python src/main_v5.py` ✅ **v5 is deployed and running**
5. Commit generated markdown to `Published Updates/`
6. Pull with rebase + push to v5-development branch

## Web UI & Cloudflare Pages Deployment

**Web UI Location**: `config/web-ui/` and `index.html` (root)
**Live URL**: https://daily-news-agent.pages.dev/
**Hosting**: Cloudflare Pages (free, private repo, auto-deploys on push)

### Available Web Pages

Web UI at https://daily-news-agent.pages.dev/ with five main pages:

1. **Homepage** - Navigation hub
2. **Feed Manager** (`config-unified.html`) - Manage 100+ feeds with health stats, toggle switches, bulk actions
3. **Email Archive** (`email-archive.html`) - Browse past daily updates by month/version
4. **V5 Recipients** (`v5-recipients.html`) - Add/remove email recipients, commits to git
5. **V5 Settings** (`v5-settings.html`) - Configure tone and feature toggles, commits to git

See [config/web-ui/NAVIGATION.md](config/web-ui/NAVIGATION.md) for complete navigation map.

### Cloudflare Pages Setup

**Deployment**: Free hosting, auto-deploys on push to v5-development, serves at https://daily-news-agent.pages.dev/

**Architecture**: GitHub Actions (5 AM) → Commits output → GitHub push → Cloudflare auto-deploy (~30s) → Live site

**Quick setup** (one-time):
1. Create account at https://dash.cloudflare.com/sign-up
2. Workers & Pages → Create → Connect GitHub → Select repo
3. Build config: Framework=None, Build command=(blank), Output dir=`/`, Branch=`v5-development`
4. Optional: Enable Cloudflare Access for authentication (free for 50 users)

**Local viewing**:
```bash
open index.html
# Or: python3 -m http.server 8000
```

### Email Archive System

**How it works**:
1. Every run (local or GitHub Actions) generates HTML email
2. HTML saved to `Published Updates/email-html/YYYY-MM-DD-v5-email.html`
3. Files committed to git (tracked in repo)
4. Cloudflare auto-deploys updated files
5. Archive page automatically discovers and displays all emails

**Archive file naming**:
- v2 emails: `YYYY-MM-DD-email.html`
- v4 emails: `YYYY-MM-DD-v4-email.html`
- v5 emails: `YYYY-MM-DD-v5-email.html`

**Implementation**: See [src/utils/email_sender_v5.py](src/utils/email_sender_v5.py) - `_save_email_archive()` method

## Adding New Content Sources

### Add RSS Feed

Edit `config/sources-v5.yaml`:
```yaml
categories:
  your_category:
    priority: high
    word_target: 400
    keywords: [keyword1, keyword2]
    sources:
      - name: "Source Name"
        url: "https://example.com/feed.xml"
        html_url: "https://example.com/"
        type: rss
        priority: high
```

### Add New Category

**Four files to update** (production v5 only):
1. [config/sources-v5.yaml](config/sources-v5.yaml) - Add category with sources
2. [src/main_v5.py](src/main_v5.py) - Add to `_consolidate_categories()` (~line 117) and `word_targets` dict (~line 223)
3. [config/templates/daily-update-v5.md](config/templates/daily-update-v5.md) - Add `{category_name_content}` placeholder
4. [src/generators/markdown_v5.py](src/generators/markdown_v5.py) - Add to `section_configs` dict

**Note**: Legacy v4/v2 files follow similar pattern but are deprecated

### Add Reddit Subreddit

Add to `config/sources-v5.yaml` under appropriate category:
```yaml
sources:
  - name: "r/SubredditName"
    url: "https://www.reddit.com/r/SubredditName/.rss"
    type: reddit
    priority: high
```

**Rate Limiting**: Reddit returns 429 errors after ~15-20 rapid requests. System handles gracefully and continues with collected articles. Automated runs typically don't hit limits.

## V5 Features (Production System)

### Multi-Recipient Email Support
**File**: [src/utils/email_sender_v5.py](src/utils/email_sender_v5.py)

Primary v5 feature - send daily updates to multiple email addresses:
- Recipients stored in `config/v5-recipients.json` (JSON array)
- Web UI for managing recipients: `config/web-ui/v5-recipients.html`
- SMTP sends to all recipients in single session
- Email subject: "Update Agent Email v5 beta - DDD MMM DD"
- From name: "My Update V5"

### Settings Configuration
**File**: `config/v5-settings.json`

JSON-based feature toggles and configuration:
- **Meta-summary tone**: analytical, conversational, or mixed
- **Readwise toggle**: Enable/disable Readwise highlights and reader
- **Stoicism toggle**: Enable/disable Daily Stoicism section
- Web UI for managing settings: `config/web-ui/v5-settings.html`
- Settings loaded at runtime via `_load_settings()` in [main_v5.py](src/main_v5.py)

### Theme Tracking System
**File**: [src/processors/theme_tracker_v5.py](src/processors/theme_tracker_v5.py)

Tracks recurring themes across 7 days of articles to provide context for meta-summaries:
- Stores daily themes in `cache/themes/theme_history.json`
- Extracts themes from article titles and categories
- Provides week context for meta-summary generation
- Auto-cleans entries older than 7 days

### Meta-Summary Generation
**Implementation**: [main_v5.py:248-258](src/main_v5.py#L248-258)

AI-generated synthesis of the day's news across all categories:
- Uses theme tracker for week context
- Generated by Claude Sonnet 4 (400 token limit)
- **Tone configurable** via `v5-settings.json` (analytical/conversational/mixed)
- Identifies cross-category patterns and trends
- Placed at top of daily update for quick overview

### Readwise Integration
**File**: [src/collectors/readwise_collector.py](src/collectors/readwise_collector.py)

Integrates personal reading highlights and Reader articles:
- Fetches daily highlights from Readwise API
- Retrieves articles from Readwise Reader
- Requires `READWISE_API_KEY` in `.env`
- **Can be disabled** via `features.readwise_enabled` in `v5-settings.json`
- Gracefully disabled if API key not present

### Feed Status Monitoring
**File**: [src/utils/feed_status_generator.py](src/utils/feed_status_generator.py)

Generates web UI showing feed health status:
- Tracks success/failure/empty status for each feed
- Outputs JSON to `config/feed-status.json`
- Web UI viewable at `config/web-ui/feed-status.html`
- Helps identify broken or stale feeds

### Enhanced Caching
**Files**: [src/utils/cache.py](src/utils/cache.py)

Two-tier caching system:
- `APIResponseCache`: Caches AI API responses (24-hour TTL)
- `ContentCache`: Caches article content to reduce fetching
- Significantly reduces API costs and runtime
- Cache directory: `cache/` (git-ignored)

## Key Configuration Changes

### Recent Customizations (v5)

1. **Multi-Recipient Email**: JSON-based recipients file (`config/v5-recipients.json`)
2. **Settings Configuration**: JSON-based feature toggles (`config/v5-settings.json`)
3. **Email Subject**: "Update Agent Email v5 beta - DDD MMM DD" format
4. **Deduplication**: Disabled in test mode for fuller previews
5. **Meta-Summary Tone**: Configurable via settings (analytical/conversational/mixed)
6. **Optional Features**: Readwise and Stoicism can be toggled on/off

### Recent Customizations (v4)

1. **Deduplication**: 7 days → 24 hours (`src/utils/deduplication.py:30`)
2. **Email Sender**: Dynamic subject with date/time, "My Update" from name (`src/utils/email_sender.py`)
3. **Stoicism Formatting**: Removed blockquote indentation (`src/generators/markdown_v2.py:139-147`)
4. **Agentic Coding Category**: New 400-word section for AI coding tools (7 subreddits)

### Email Configuration

Email types distinguished by version and `UPDATE_SOURCE` environment variable:

**V5 (Production)**:
- **GitHub Actions**: `UPDATE_SOURCE=Web` → Subject: "Update Agent Email v5 beta - DDD MMM DD"
- **Local macOS**: `UPDATE_SOURCE=Local` → Subject: "Update (Local): DDD MMM DD"
- **From Name**: "My Update V5"
- **Recipients**: Loaded from `config/v5-recipients.json`

**V4 (Legacy)**:
- **GitHub Actions**: `UPDATE_SOURCE=Web` → Subject: "Update: Day MM-DD-YY at time"
- **Local macOS**: `UPDATE_SOURCE=Local` → Subject: "Update (Local): Day MM-DD-YY at time"
- **From Name**: "My Update"
- **Recipients**: Single recipient from `GMAIL_ADDRESS` env var

Email sending logic in `src/utils/email_sender_v5.py:50-120` (v5) and `src/utils/email_sender.py:50-80` (v4)

## Project Structure

```
daily-news-agent/
├── .github/workflows/
│   ├── daily-update-v5.yml          # V5 GitHub Actions (ACTIVE - 5 AM EST)
│   └── daily-update.yml              # V4 GitHub Actions (DISABLED)
├── config/
│   ├── sources-v5.yaml               # v5: 100+ feeds (production)
│   ├── sources-v4.yaml               # v4: 100+ feeds (legacy)
│   ├── sources-v2.yaml               # v2: 77+ RSS feeds (legacy)
│   ├── v5-recipients.json            # v5: Multi-recipient email config
│   ├── v5-settings.json              # v5: Feature toggles and settings
│   ├── templates/
│   │   ├── daily-update-v5.md        # v5 markdown template
│   │   ├── daily-update-v4.md        # v4 markdown template
│   │   └── daily-update-v2.md        # v2 markdown template
│   ├── feed-status.json              # Feed health monitoring data
│   └── web-ui/
│       ├── config-unified.html       # Feed Manager (unified interface)
│       ├── email-archive.html        # Email Archive
│       ├── v5-recipients.html        # V5 Recipients Manager
│       └── v5-settings.html          # V5 Settings Manager
├── src/
│   ├── main_v5.py                    # v5 main orchestrator (production)
│   ├── main_v4.py                    # v4 main orchestrator (legacy)
│   ├── main_v2.py                    # v2 main orchestrator (legacy)
│   ├── collectors/
│   │   ├── rss_collector_enhanced.py # Concurrent RSS/Reddit collection
│   │   ├── readwise_collector.py     # Readwise integration
│   │   ├── weather_api.py
│   │   ├── supplementary.py
│   │   └── on_this_day_api.py
│   ├── processors/
│   │   ├── ai_summarizer_v5.py       # v5 AI summarizer
│   │   ├── ai_summarizer_v4.py       # v4 AI summarizer
│   │   ├── ai_summarizer_v2.py       # v2 AI summarizer
│   │   ├── theme_tracker_v5.py       # v5: 7-day theme tracking
│   │   └── theme_tracker_v4.py       # v4: 7-day theme tracking
│   ├── generators/
│   │   ├── markdown_v5.py            # v5 markdown generator
│   │   ├── markdown_v4.py            # v4 markdown generator
│   │   └── markdown_v2.py            # v2 markdown generator
│   └── utils/
│       ├── deduplication.py          # 24-hour hash-based cache
│       ├── content_filter.py         # Keyword-based filtering
│       ├── email_sender_v5.py        # v5: Multi-recipient Gmail SMTP
│       ├── email_sender.py           # v4: Single-recipient Gmail SMTP
│       ├── cache.py                  # API response caching
│       ├── feed_status_generator.py  # Feed health monitoring
│       └── feed_discovery.py         # RSS feed discovery tool
├── Published Updates/                # Git-tracked daily outputs (YYYY-MM-DD-daily-update.md)
│   └── email-html/                   # HTML email archives
├── cache/
│   ├── api/                          # API response cache (24h TTL)
│   ├── content/                      # Article content cache
│   ├── seen_articles/                # Deduplication cache (24h window)
│   └── themes/                       # 7-day theme history
├── v5-recipients.json                # v5: Recipients fallback (root)
├── requirements.txt
└── .env                              # Git-ignored (API keys)
```

## Troubleshooting

### GitHub Actions Failures
- Check workflow run logs: https://github.com/jonsims/daily-news-agent/actions
- Verify all GitHub Secrets are set correctly
- Common issue: Expired API keys or invalid Gmail app password

### V5 Multi-Recipient Email Issues
- **No emails sent**: Check `config/v5-recipients.json` exists and has valid JSON
- **Missing recipients**: Verify JSON array format is correct
- **SMTP errors**: Check `GMAIL_APP_PASSWORD` secret is valid
- **Wrong recipients**: Check both `config/v5-recipients.json` and root `v5-recipients.json`

### V5 Settings Not Applied
- **Features not toggling**: Check `config/v5-settings.json` syntax
- **Wrong tone**: Verify `meta_summary.tone` is "analytical", "conversational", or "mixed"
- **Readwise still running**: Ensure `features.readwise_enabled` is `false` and API key is removed or settings file exists

### Content Issues
- **Too few articles**: Clear deduplication cache or increase window
- **Reddit 429 errors**: Expected during rapid testing, auto-handled in production
- **Weather API fails**: Graceful degradation (continues without weather)
- **Wikipedia "On This Day" 403**: Falls back to History API

### Local vs Cloud Sync
- GitHub Actions commits to `Published Updates/` → Pull locally with `git pull`
- Local system can be disabled: `launchctl unload ~/Library/LaunchAgents/com.jonsims.dailynews.plist`

### Test Mode File Conflicts (FIXED October 2025)
Test mode creates separate files: `YYYY-MM-DD-TEST-daily-update.md` and `YYYY-MM-DD-v5-test-email.html` to avoid git conflicts with production runs.

## Cost & Performance

**Monthly Costs**: ~$4.50
- Claude API: ~$0.12/day = ~$3.60/month
- OpenAI API: ~$0.03/day = ~$0.90/month (rarely used)
- GitHub Actions: $0 (60 min/month of 2,000 free)

**Performance**:
- Concurrent RSS collection reduces runtime
- 24-hour API cache prevents redundant calls
- 24-hour deduplication cache increases article diversity (disabled in v5 test mode)

## Important Architectural Patterns

### Component Initialization Pattern
All major components follow this pattern (see [main_v5.py:46-88](src/main_v5.py#L46-88)):
1. Load environment variables via `load_dotenv()`
2. Load settings from `config/v5-settings.json` (v5 only)
3. Initialize collectors with API keys from environment
4. Set up graceful fallbacks (e.g., OpenAI if Claude fails)
5. Initialize caching if available
6. Log initialization status

### Error Handling Philosophy
- **Graceful degradation**: System continues if non-critical components fail
- **Fallback chains**: Claude → OpenAI → Mock responses
- **Logging over exceptions**: Log errors but continue processing
- **Examples**:
  - Weather API fails → Skip weather section, continue
  - Reddit rate limits → Use collected articles, continue
  - Readwise disabled → Skip Readwise sections, continue
  - Settings file missing → Use defaults, continue

### Concurrent Collection Pattern
See [rss_collector_enhanced.py](src/collectors/rss_collector_enhanced.py):
- Uses `ThreadPoolExecutor` for parallel RSS fetching
- Significantly reduces collection time (from ~5min to ~1min)
- Handles individual feed failures gracefully
- Tracks feed status for monitoring

### Category Consolidation Pattern
See [main_v5.py:117-149](src/main_v5.py#L117-149):
- Raw categories from config → Consolidated output categories
- Allows flexible source organization while maintaining clean output
- Example: Multiple tech sources → Single "AI & Technology" section

### Caching Strategy
Three-tier caching system:
1. **Article deduplication** (24h): Prevents showing same article twice (disabled in v5 test mode)
2. **API response cache** (24h): Reduces AI API costs
3. **Content cache**: Reduces RSS refetching within run

### Settings Management Pattern (v5)
See [main_v5.py:105-135](src/main_v5.py#L105-135):
- Settings loaded from JSON files at runtime
- Fallback to defaults if file missing or invalid
- Two-file strategy: `config/v5-settings.json` (primary), root fallback
- Settings validate and provide graceful degradation
- Web UI for easy management without code changes

### Code Organization Rules
- **v5 files**: Production code - all current development happens here
- **v4 files**: Legacy code - workflow disabled, preserved for reference
- **v2 files**: Legacy code - preserved for reference, no longer in use
- **Shared utilities**: In `utils/` - used by all versions
- **Version-specific code**: Suffixed with `_v2`, `_v4`, or `_v5`
- **New features**: Always add to v5 files

## Version

**Current Production (v5-development branch)**: v5 (v0.5)
**Legacy (v4-development branch)**: v4 (v0.4) - Workflow disabled
**Legacy (main branch)**: v2 (v0.3) - No longer in use

See [src/utils/version.py](src/utils/version.py) for version string used in output files.

---

## Recent Code Quality Improvements

**October 17, 2025 - Phase 1 Cleanup**:
- Removed unreachable code and debug prints
- Test mode file separation (prevents git conflicts)
- Fixed version comments and test class names
- Result: Cleaner code, no workflow exit code 128 errors
