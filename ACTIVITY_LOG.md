# Activity Log

Track changes made to the GrantBot project. Add your entries at the top.

---

## January 15, 2025 - @enoyes

### Initial Setup
- Cloned repo from https://github.com/jonsims/grantbot.git to `~/Projects/grantbot`
- Installed Python dependencies via `pip3 install -r requirements.txt`
- Created `.env` file with Anthropic and OpenAI API keys
- Set up `git sync` alias for quick commits (`git add -A && git commit -m 'updates' && git push`)

### Planning
- Reviewed codebase structure (this is a Daily News Agent that we're repurposing for grants)
- Defined Generator AI Lab profile:
  - Entity type: University/College
  - Focus: Entrepreneurship, innovation, AI impact, pedagogical research (interdisciplinary)
  - Grant sizes: All ($1K to $1M+)
- Identified grant sources to add: grants.gov, NSF, foundations, etc.

### Next Steps
- Create `config/sources-grants.yaml` with grant RSS feeds
- Build grants.gov collector
- Create organization profile config
