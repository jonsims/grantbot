# Daily News Agent - Changelog

## Version 0.3 - September 27, 2025

### Major Features Added

**1. Article Deduplication System**
- Prevents the same articles from appearing in multiple daily updates
- 7-day cache of seen articles (automatically cleaned)
- Tracks articles by URL and title hash
- Location: `src/utils/deduplication.py`

**2. Version Management**
- Tracks version numbers across updates
- Current version: v0.3
- Increments by 0.1 per significant change
- Version displayed in update header
- Location: `src/utils/version.py`

**3. Test Mode**
- Generate test updates with "Test" in title
- Command: `python3 src/main_v2.py --test`
- Useful for previewing changes before production

**4. Reddit Feed Configuration**
- Configurable subreddit list in markdown file
- Upvote thresholds per subreddit
- Content filtering rules
- Location: `config/Reddit Feeds for Update.md`

**5. Automated Daily Schedule**
- Runs automatically at 4:00 AM every day
- macOS LaunchAgent integration
- Logging to `logs/` directory
- Setup instructions in `AUTOMATION_SETUP.md`

### Format Changes

**1. Heading Style**
- Changed from markdown `###` to HTML-styled headings
- Style: 1.3em font, bold, underlined
- Thin line separators between sections (1px solid #ddd)
- Better control over visual appearance

**2. List Format**
- Removed bullet points (•)
- Clean list format with blank lines between items
- Format: `[Title](link) - Summary. — Source`
- More readable in both Obsidian and email clients

**3. Header Information**
- Added version number to header
- Format: `*Generated at {time} | {articles} articles analyzed | {version}*`
- Test mode adds "Test " prefix to title

### Files Added

- `src/utils/deduplication.py` - Article deduplication system
- `src/utils/version.py` - Version management
- `config/Reddit Feeds for Update.md` - Reddit feed configuration
- `config/version.json` - Version tracking file
- `run_daily_update.sh` - Automation runner script
- `com.jonsims.dailynewsagent.plist` - LaunchAgent configuration
- `AUTOMATION_SETUP.md` - Setup instructions
- `CHANGELOG.md` - This file
- `logs/` - Directory for automation logs

### Files Modified

- `src/main_v2.py` - Added deduplication, version tracking, test mode
- `src/generators/markdown_v2.py` - Updated heading style, version display
- `src/processors/ai_summarizer_v2.py` - Clean list format (no bullets)
- `config/templates/daily-update-v2.md` - Updated template with version
- `CLAUDE.md` - Updated documentation
- `README.md` - Updated with new features

### Breaking Changes

None - all changes are backward compatible

### Known Issues

- OpenAI API quota limits may cause fallback to mock responses
- Consider adding Claude API key as backup

### Next Steps (Future Enhancements)

1. Implement Reddit smart filtering with upvote thresholds
2. Add Readwise integration
3. Auto-generate Obsidian wiki links for companies/people
4. Priority indicators for must-read articles
5. Weekly digest summary

---

## Version 0.2 - September 26, 2025

### Features
- 8 consolidated categories
- Clean bullet-point format with embedded links
- Weather for Framingham, MA (01701)
- Daily Stoicism quotes
- Email delivery

### Initial Setup
- RSS feed collection from 77+ sources
- OpenAI API integration
- 24-hour caching system
- Obsidian frontmatter support

---

*For detailed usage instructions, see CLAUDE.md and README.md*