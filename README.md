# GrantBot

AI-powered grant discovery and analysis for **Generator AI Lab at Babson College**.

## What It Does

GrantBot automatically:
1. **Collects** grant opportunities from federal sources (grants.gov, NSF) and foundations (Kauffman)
2. **Filters** for eligibility and relevance to our focus areas
3. **Analyzes** each match with AI for fit scoring and action items
4. **Delivers** a prioritized digest via email

## Quick Start

```bash
# Clone the repo
git clone https://github.com/jonsims/grantbot.git
cd grantbot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (CLAUDE_API_KEY, OPENAI_API_KEY, GMAIL_*)

# Run grant discovery
python src/main.py --test
```

## Project Structure

```
src/
├── main.py              # Entry point
├── collectors/          # Data fetching from grant sources
│   ├── grants_gov.py    # Federal grants (grants.gov)
│   ├── nsf.py           # National Science Foundation
│   └── foundations.py   # Private foundations (Kauffman, etc.)
├── processors/          # Grant analysis
│   ├── matcher.py       # Match grants to org profile
│   └── analyzer.py      # AI-powered deep analysis
├── generators/          # Output formatting
│   └── digest.py        # Email/markdown digest
└── utils/               # Shared utilities
    ├── cache.py         # API response caching
    ├── deduplication.py # Track seen grants
    └── email_sender.py  # Email delivery

config/
├── org-profile.yaml     # Our organization profile for matching
├── sources-grants.yaml  # Which sources to check
└── version.json         # Current version
```

## Configuration

### Organization Profile (`config/org-profile.yaml`)
Defines Generator AI Lab for grant matching:
- **Entity type**: University (Babson College)
- **Location**: Massachusetts
- **Focus areas**: Entrepreneurship, AI, Innovation, Pedagogy
- **Grant sizes**: $1K - $1M+

### Grant Sources (`config/sources-grants.yaml`)
- **Federal**: grants.gov, NSF
- **Foundations**: Kauffman Foundation
- **State**: MassTech (Massachusetts)

## Development Status

**Current Version: 0.2.0**

| Milestone | Status | Description |
|-----------|--------|-------------|
| M1: Foundation | 🔨 In Progress | grants.gov collector, basic matching |
| M2: Analysis | ⏳ Planned | Full analysis pipeline, fit scoring |
| M3: Delivery | ⏳ Planned | Email digest, automation |
| M4: Expansion | ⏳ Planned | NSF, more foundations, historical tracking |

## Reference Code

The `archive/` folder contains the original daily-news-agent codebase for reference. Key patterns:
- `archive/src/collectors/rss_collector_enhanced.py` - Feed collection with caching
- `archive/src/processors/ai_summarizer_v5.py` - LLM-based analysis patterns
- `archive/src/utils/email_sender_v5.py` - Email delivery

## Resources

See [PRD.md](PRD.md) for full product requirements and [Appendix A](PRD.md#appendix-a-potential-tools--libraries) for useful GitHub repos.

## Team

- Jon
- Erik
