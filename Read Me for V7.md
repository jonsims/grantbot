# Daily News Agent V7 - User Guide

Welcome! This guide explains how to use the Daily News Agent V7 to get personalized daily news summaries delivered to your email and Obsidian vault.

---

## What Does V7 Do?

Every day, V7 automatically:

1. **Collects news** from 90+ RSS feeds across topics you care about (AI, tech, business, space, etc.)
2. **Extracts full articles** when RSS feeds only provide snippets
3. **Summarizes everything** using AI into a digestible daily digest
4. **Sends you an email** with the formatted summary
5. **Saves to Obsidian** so you can reference articles later

---

## Quick Start

### Run V7 from Claude Code

Use this slash command:

```
/run-v7-daily
```

This runs V7 in **test mode**, which:
- Sends email only to jon.sims@gmail.com
- Saves the daily summary to your Obsidian vault
- Exports individual articles you might want to read later

---

## Where to Find Your News

### Email
Check your inbox for emails from **"Daily Email V7 TEST"** (test mode) or **"Daily Email V7"** (production).

### Obsidian Vault

| What | Location |
|------|----------|
| Daily Summary | `Daily Emails/2026-01-11 Daily News.md` |
| Individual Articles | `Daily Emails/Articles/2026-01-11/` folder |

The daily summary includes all categories in one file. Individual articles are saved separately so you can keep the ones you find valuable.

---

## Understanding the Output

### Daily Summary Structure

Each daily summary includes sections like:

- **AI & Technology** - Latest in artificial intelligence and tech
- **Moonshot Strategy** - Breakthrough ideas and innovations
- **Market & Business** - Financial and business news
- **Academia & Research** - Academic developments
- **Space News** - Space exploration updates
- **Good News** - Positive stories to brighten your day
- And more...

### Individual Articles

Articles saved to Obsidian include:
- **Title** and **source**
- **Full extracted text** (when available)
- **Link to original** article
- **Tags** for easy searching

Only articles where we successfully extracted the full text get saved (about 60-70% of articles). Paywalled sites like NYT, WSJ, etc. are automatically skipped.

---

## Automatic vs Manual Runs

### Automatic (GitHub Actions)
V7 can run automatically every morning via GitHub Actions. Currently this sends emails but does NOT save to your local Obsidian vault (since GitHub can't access your computer).

### Manual (Local)
Running `/run-v7-daily` on your computer:
- Sends email
- Saves to Obsidian vault
- Exports individual articles

**Tip:** Run V7 locally when you want articles saved to Obsidian.

---

## Customization

### Change Where Files Are Saved

Edit `config/v7-settings.json`:

```json
"obsidian": {
  "vault_path": "/Users/jonsims/2026 Agent",
  "news_folder": "Daily Emails"
}
```

### Turn Off Article Export

If you only want the daily summary (not individual articles):

```json
"article_export": {
  "enabled": false
}
```

### Turn Off Obsidian Entirely

```json
"obsidian": {
  "enabled": false
}
```

---

## Troubleshooting

### "I didn't get an email"
- Check your spam folder
- Make sure you ran V7 successfully (look for the green checkmark message)

### "No articles in my Obsidian vault"
- Make sure `obsidian.enabled` is `true` in settings
- Verify the `vault_path` points to your actual Obsidian vault folder
- Run V7 locally (not via GitHub Actions)

### "Only some articles were exported"
This is normal! V7 only exports articles where it could extract the full text. Paywalled sites and sites that block scraping are automatically skipped.

---

## Technical Details (Optional Reading)

### What's New in V7 vs V5

| Feature | V5 | V7 |
|---------|----|----|
| AI Model | Claude Sonnet 4 | Claude 3.5 Haiku |
| Fallback Model | GPT-4 | GPT-4o Mini |
| Full-text extraction | No | Yes (Trafilatura) |
| Obsidian integration | No | Yes |
| Individual article export | No | Yes |

### File Locations

| File | Purpose |
|------|---------|
| `config/v7-settings.json` | All V7 configuration |
| `config/v7-recipients.json` | Email recipient list |
| `src/main_v7.py` | Main V7 program |
| `Published Updates/` | Archive of all generated updates |

### Command Line Options

If running manually from terminal:

```bash
# Test mode (recommended)
python3 src/main_v7.py --test

# Production mode
python3 src/main_v7.py

# Skip full-text extraction (faster)
python3 src/main_v7.py --test --skip-fulltext

# Skip Obsidian save
python3 src/main_v7.py --test --skip-obsidian
```

---

## Need Help?

Ask Claude Code! Just describe what you're trying to do or what's not working.

---

*Last updated: January 11, 2026*
