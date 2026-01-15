# Feed Suggestions Feature

## Overview

The feed suggestions feature automatically discovers and recommends related RSS feeds and subreddits that you might want to add to your daily news digest. Suggestions appear in the web UI with one-click adding capability.

## How It Works

### Discovery Strategies

The system uses multiple strategies to find relevant feeds:

1. **Curated Feeds** (High Priority)
   - Pre-vetted, high-quality feeds from trusted sources
   - Organized by category (AI, tech tools, academic research, etc.)
   - Examples: Anthropic Blog, Hugging Face, Nature AI, WSJ Tech

2. **Related Subreddits**
   - Reddit communities aligned with each category
   - Automatically formatted as RSS feeds
   - Examples: r/LocalLLaMA, r/MachineLearning, r/AskScience

3. **Same-Domain Feeds** (Currently Disabled)
   - Discovers other feeds from domains you already use
   - Disabled by default for performance (can be re-enabled)

### Suggestion Metadata

Each suggestion includes:
- **Name**: Feed or subreddit name
- **Description**: What the feed covers
- **Estimated posts/week**: Activity level indicator
- **Sample headline**: Preview of content (when available)
- **Preview link**: URL to browse the feed before adding
- **Confidence badge**: Quality indicator (high/medium)

## Using Suggestions in the Web UI

### Viewing Suggestions

1. Open [config/web-ui/index.html](config/web-ui/index.html) in your browser
2. Authenticate with your GitHub Personal Access Token
3. Scroll to any category that has suggestions
4. Look for the **"💡 Suggested Feeds (N)"** section at the bottom
5. Click to expand and view suggestions

### Adding a Suggested Feed

1. Browse suggested feeds for a category
2. Click **"+ Add Feed"** button on any suggestion
3. The feed is immediately added to your configuration
4. Click **"Save to GitHub"** at the bottom of the page to commit changes
5. Next daily run will include articles from the new feed

## Automatic Weekly Updates

Suggestions are refreshed automatically every Monday at 3:00 AM EST via GitHub Actions.

**Workflow**: [.github/workflows/weekly-feed-suggestions.yml](.github/workflows/weekly-feed-suggestions.yml)

### Manual Refresh

To manually regenerate suggestions:

**Option 1: GitHub Actions (Web)**
1. Go to https://github.com/jonsims/daily-news-agent/actions
2. Click "Weekly Feed Suggestions"
3. Click "Run workflow" → Select branch: `v4-development`

**Option 2: Local Command Line**
```bash
cd /path/to/daily-news-agent
python3 src/utils/feed_discovery.py
```

This generates: `config/feed-suggestions.json`

## Customizing Suggestions

### Adding More Curated Feeds

Edit [src/utils/feed_discovery.py](src/utils/feed_discovery.py) lines 27-77:

```python
self.curated_feeds = {
    'your_category': [
        {
            'name': 'Feed Name',
            'url': 'https://example.com/feed.xml',
            'description': 'What this feed covers'
        }
    ]
}
```

### Adding More Subreddit Suggestions

Edit [src/utils/feed_discovery.py](src/utils/feed_discovery.py) lines 80-89:

```python
self.subreddit_suggestions = {
    'your_category': ['r/Subreddit1', 'r/Subreddit2']
}
```

### Re-enabling Same-Domain Discovery

Edit [src/utils/feed_discovery.py](src/utils/feed_discovery.py) line 148-151:

```python
# Change from:
def discover_same_domain_feeds(self, category: str, existing_sources: List[Dict]) -> List[Dict]:
    """Find other RSS feeds from same domains - DISABLED for speed"""
    return []

# To: (restore full implementation from git history)
```

**Note**: This significantly increases discovery time (2-5 minutes vs 1 second).

## File Structure

```
daily-news-agent/
├── config/
│   ├── feed-suggestions.json      # Generated suggestions (auto-updated weekly)
│   └── web-ui/
│       ├── index.html              # Web UI (with suggestion styles)
│       └── config-editor.js        # JavaScript (loads & displays suggestions)
├── src/utils/
│   └── feed_discovery.py           # Discovery script
└── .github/workflows/
    └── weekly-feed-suggestions.yml # Auto-refresh workflow
```

## Troubleshooting

### No Suggestions Appear in Web UI

1. Check if `config/feed-suggestions.json` exists
2. Run discovery script manually: `python3 src/utils/feed_discovery.py`
3. Refresh the web page and clear browser cache
4. Check browser console for errors (F12 → Console tab)

### Suggestions File Not Generated

1. Ensure you're on `v4-development` branch
2. Check `config/sources-v4.yaml` exists
3. Install dependencies: `pip install -r requirements.txt`
4. Check logs when running: `python3 src/utils/feed_discovery.py`

### GitHub Actions Workflow Not Running

1. Verify workflow file exists: `.github/workflows/weekly-feed-suggestions.yml`
2. Check Actions tab: https://github.com/jonsims/daily-news-agent/actions
3. Ensure workflow is enabled (not disabled)
4. Manually trigger via "Run workflow" button

### Suggestions Already in Config

The system automatically filters out feeds you already have. If you see no suggestions:
- You may have already added most relevant feeds for that category
- Try adding more curated feeds to `feed_discovery.py`

## Performance Notes

- Discovery runs in ~1-2 seconds (optimized for speed)
- Suggestions cached in JSON file (no repeated API calls)
- Same-domain discovery disabled by default (saves ~2 minutes)
- Weekly refresh prevents stale suggestions

## Future Enhancements

Potential improvements:
- AI-powered suggestions based on article content analysis
- Cross-category recommendations
- Popularity metrics from feed aggregators
- User voting/rating system for suggestions
- Import from OPML files or feed directories

---

**Version**: 1.0
**Last Updated**: 2025-10-10
**Branch**: v4-development
