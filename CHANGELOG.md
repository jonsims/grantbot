# GrantBot Changelog

## v0.2.0 - January 15, 2026

### Major Restructure
Cleaned up codebase from daily-news-agent fork. Moved all news-specific code to `archive/` for reference.

**New Structure:**
- `src/collectors/` - Grant source collectors (stubs)
  - `grants_gov.py` - Federal grants from grants.gov
  - `nsf.py` - National Science Foundation
  - `foundations.py` - Private foundations (Kauffman focus)
- `src/processors/` - Grant analysis
  - `matcher.py` - Match grants against org profile with `OrgProfile` dataclass
  - `analyzer.py` - LLM-powered deep analysis
- `src/generators/` - Output generation
  - `digest.py` - Email and markdown digest
- `src/main.py` - Working entry point with full pipeline scaffold

**New Configuration:**
- `config/org-profile.yaml` - Generator AI Lab profile (Babson College)
  - Focus areas: entrepreneurship, AI, innovation, pedagogy
  - Entity type: university
  - Location: Massachusetts
- `config/sources-grants.yaml` - Grant source configuration
  - Federal: grants.gov, NSF
  - Foundations: Kauffman
  - State: MassTech

**Kept from Original:**
- `src/utils/cache.py` - API response caching
- `src/utils/deduplication.py` - Track seen grants
- `src/utils/email_sender.py` - Email delivery
- `src/utils/version.py` - Version management

**Archived:**
- All RSS/news collectors
- All news processors (summarizers, theme trackers)
- All markdown generators (v1-v5)
- News-specific configs (sources-*.yaml, content_priorities)
- News documentation (FEED_SUGGESTIONS, All_Feeds, etc.)
- Cloudflare workers

### Documentation
- Updated `CLAUDE.md` for GrantBot context
- Added `README.md` with quickstart guide
- `PRD.md` updated with Appendix A (potential tools/libraries from GitHub)

---

## v0.1.0 - January 15, 2026

### Initial Fork
Forked from daily-news-agent v5 codebase.
- Full news agent functionality
- Added PRD.md with GrantBot requirements
- Added potential GitHub tools research to PRD Appendix A

**Tag:** `v0.1` - Available for reference if needed (`git checkout v0.1`)
