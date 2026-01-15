# GrantBot

AI-powered grant discovery and analysis for Generator AI Lab at Babson College.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run grant discovery
python src/main.py
```

## Project Structure

```
src/
├── collectors/        # Data fetching from grant sources
│   ├── grants_gov.py  # grants.gov API collector
│   ├── nsf.py         # NSF Awards API collector
│   └── foundations.py # Foundation data collector
├── processors/        # Grant analysis and matching
│   ├── matcher.py     # Match grants to org profile
│   └── analyzer.py    # Deep analysis of matches
├── generators/        # Output formatting
│   └── digest.py      # Email digest generator
└── utils/             # Shared utilities
    ├── cache.py       # API response caching
    ├── deduplication.py # Track seen grants
    ├── email_sender.py  # Email delivery
    └── version.py     # Version tracking

config/
├── org-profile.yaml   # Organization profile for matching
├── sources-grants.yaml # Grant source configuration
└── version.json       # Current version
```

## Configuration

### Organization Profile (config/org-profile.yaml)
Defines who we are for grant matching:
- Entity type (university)
- Focus areas (entrepreneurship, AI, innovation, pedagogy)
- Location (Massachusetts)
- Grant size preferences

### Grant Sources (config/sources-grants.yaml)
Defines where to look for grants:
- grants.gov (federal)
- NSF
- Foundations (Kauffman, etc.)
- State agencies (MassTech, MLSC)

## Environment Variables

```
CLAUDE_API_KEY=     # For grant analysis
OPENAI_API_KEY=     # Backup LLM
GMAIL_ADDRESS=      # For email delivery
GMAIL_APP_PASSWORD= # Gmail app password
```

## Archive

The `archive/` folder contains the original daily-news-agent code for reference. Key patterns to adapt:
- `archive/src/collectors/rss_collector_enhanced.py` - Feed collection with caching
- `archive/src/processors/ai_summarizer_v5.py` - LLM-based analysis
- `archive/src/utils/email_sender_v5.py` - Email delivery

## Development Milestones

See PRD.md for full details:
- **M1**: grants.gov collector + basic matching
- **M2**: Full analysis pipeline + fit scoring
- **M3**: Email digest + automation
- **M4**: Add NSF, foundations, historical tracking
