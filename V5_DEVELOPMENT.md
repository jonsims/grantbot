# V5 Development Guide
**Created**: October 15, 2025
**Branch**: v5-development
**Status**: 🧪 EXPERIMENTAL - Testing New Features

---

## Overview

V5 is an experimental branch for testing new features before adding them to production (v4). The main feature being tested is **multi-recipient email support**, allowing the daily update to be sent to multiple email addresses simultaneously.

---

## Key V5 Features

### 1. Multi-Recipient Email Support

**What it does**: Sends the daily update email to multiple recipients instead of just one.

**Configuration**:
- New environment variable: `GMAIL_ADDRESSES_V5`
- Format: Comma-separated list of email addresses
- Example: `email1@gmail.com,email2@gmail.com,email3@gmail.com`

**Local Setup** (`.env` file):
```bash
GMAIL_ADDRESSES_V5=jon.sims@gmail.com,other@example.com,third@example.com
```

**GitHub Setup** (GitHub Secrets):
1. Go to: https://github.com/jonsims/daily-news-agent/settings/secrets/actions
2. Click "New repository secret"
3. Name: `GMAIL_ADDRESSES_V5`
4. Value: `email1@gmail.com,email2@gmail.com,email3@gmail.com`
5. Click "Add secret"

### 2. V5 TEST Email Labeling

All v5 emails are clearly marked:
- Email subject: `V5 TEST: Day MM-DD-YY at time`
- Email header: Red banner with "🧪 V5 TEST VERSION - Experimental Build"
- From name: "My Update V5"

This makes it easy to distinguish v5 test emails from v4 production emails.

---

## Running V5

### Local Testing

```bash
# Run v5 in test mode (adds "Test" to title, sends email)
python3 src/main_v5.py --test

# Run v5 in production mode (sends to all recipients)
python3 src/main_v5.py

# Test all v5 components
python3 src/main_v5.py --test-components
```

### GitHub Actions

**Workflow**: `.github/workflows/daily-update-v5.yml`
**Schedule**: Daily at 5:00 AM EST (10:00 AM UTC) - 1 hour after v4
**Trigger**: Automatic cron + manual dispatch

**Manual Trigger**:
1. Go to: https://github.com/jonsims/daily-news-agent/actions
2. Click "Daily News Update V5 (TEST)"
3. Click "Run workflow" → "Run workflow"

---

## V5 vs V4 Comparison

| Feature | V4 (Production) | V5 (Experimental) |
|---------|----------------|-------------------|
| **Branch** | v4-development | v5-development |
| **Schedule** | 4:00 AM EST | 5:00 AM EST |
| **Email Recipients** | Single | Multiple |
| **Email Subject** | `Update v4: ...` | `V5 TEST: ...` |
| **Email From** | "My Update" | "My Update V5" |
| **Email Banner** | None | Red "V5 TEST" banner |
| **Output Directory** | `Published Updates/` | `Published Updates/` |
| **Status** | ✅ Production | 🧪 Experimental |

---

## File Structure

### V5-Specific Files

```
daily-news-agent/
├── src/
│   ├── main_v5.py                    # V5 main orchestrator
│   ├── processors/
│   │   ├── ai_summarizer_v5.py       # V5 AI summarizer (same as v4)
│   │   └── theme_tracker_v4.py       # Shared with v4
│   ├── generators/
│   │   └── markdown_v5.py            # V5 markdown generator
│   └── utils/
│       └── email_sender_v5.py        # V5 multi-recipient email sender
├── config/
│   ├── sources-v5.yaml               # V5 source configuration
│   └── templates/
│       └── daily-update-v5.md        # V5 markdown template
└── .github/workflows/
    └── daily-update-v5.yml           # V5 GitHub Actions workflow
```

### Shared Files (used by both v4 and v5)
- All collectors (`rss_collector_enhanced.py`, `readwise_collector.py`, etc.)
- Utilities (`deduplication.py`, `content_filter.py`, `cache.py`)
- Theme tracker (`theme_tracker_v4.py`)

---

## Testing Checklist

Before deploying a new feature from v5 to v4:

- [ ] Run `python3 src/main_v5.py --test` successfully
- [ ] Verify emails sent to all recipients
- [ ] Check email formatting and V5 TEST banner
- [ ] Run `python3 src/main_v5.py --test-components` - all pass
- [ ] Test GitHub Actions workflow manually
- [ ] Verify files committed to `Published Updates/`
- [ ] Check logs for any errors or warnings
- [ ] Confirm v4 production still running normally

---

## Environment Variables

### Required for V5
```bash
# Standard variables (same as v4)
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GMAIL_APP_PASSWORD=...

# V5-specific: Multiple recipients
GMAIL_ADDRESSES_V5=email1@gmail.com,email2@gmail.com,email3@gmail.com

# Optional
UPDATE_SOURCE=Local  # or "Web" for GitHub Actions
READWISE_API_KEY=...  # Optional
```

---

## Adding New Recipients

### Locally (`.env` file)
1. Edit `.env` file
2. Update `GMAIL_ADDRESSES_V5` with comma-separated emails
3. Save and run v5

### GitHub Actions
1. Go to: https://github.com/jonsims/daily-news-agent/settings/secrets/actions
2. Click on `GMAIL_ADDRESSES_V5` secret
3. Click "Update secret"
4. Add new email to comma-separated list
5. Click "Update secret"

---

## Promoting Features from V5 to V4

When a v5 feature is ready for production:

1. **Test thoroughly** - Run all tests, verify all scenarios
2. **Document changes** - Update CLAUDE.md and relevant docs
3. **Merge to v4** - Copy working code from v5 to v4 files
4. **Update v4 workflow** - If needed, update `.github/workflows/daily-update.yml`
5. **Test v4** - Run v4 locally to verify integration
6. **Deploy** - Push to v4-development branch
7. **Monitor** - Watch first automated run for issues

**Example**: To add multi-recipient email to v4:
1. Copy `email_sender_v5.py` logic to `email_sender.py`
2. Update `main_v4.py` to use new email features
3. Add `GMAIL_ADDRESSES_V4` secret to GitHub
4. Test locally with `python3 src/main_v4.py --test`
5. Push to v4-development

---

## Troubleshooting

### V5 Emails Not Sending
- Check `GMAIL_ADDRESSES_V5` is set correctly
- Verify `GMAIL_APP_PASSWORD` is valid
- Check logs for specific error messages
- Test with single recipient first

### V5 Workflow Not Running
- Check `.github/workflows/daily-update-v5.yml` exists
- Verify cron schedule (10:00 AM UTC = 5:00 AM EST)
- Check workflow is enabled in GitHub Actions
- Try manual trigger first

### Multiple Recipients Not Working
- Verify email list format: comma-separated, no spaces (unless in quotes)
- Check each email address is valid
- Look for SMTP errors in logs
- Test with `python3 src/utils/email_sender_v5.py` directly

---

## Future V5 Features

Potential features to test in v5:

- **Newsletter formatting** - Different email template styles
- **Personalized content** - Different summaries per recipient
- **Email scheduling** - Different times for different recipients
- **Digest mode** - Weekly summary option
- **Category filtering** - Recipients choose categories
- **Mobile optimization** - Better mobile email rendering

Add new experimental features to v5 files, test thoroughly, then promote to v4 when ready.

---

## Version History

- **October 15, 2025**: V5 created with multi-recipient email support
- Branch forked from v4-development
- First feature: Multi-recipient email via `GMAIL_ADDRESSES_V5`

---

## Support

For issues or questions about v5 development:
1. Check logs in GitHub Actions: https://github.com/jonsims/daily-news-agent/actions
2. Review v4 implementation for comparison
3. Test locally before relying on GitHub Actions
4. Document all changes for future reference

---

**Remember**: V5 is for experimentation. V4 is production. Keep v4 stable while testing new ideas in v5!
