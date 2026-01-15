# Reddit Feeds for Daily Update

This file configures which Reddit subreddits are included in your daily update and how they are filtered.

## Active Subreddits

### Learning & Knowledge
- r/todayilearned (minimum upvotes: 1000)
- r/explainlikeimfive (minimum upvotes: 500)
- r/YouShouldKnow (minimum upvotes: 500)

### Data & Guides
- r/DataIsBeautiful (minimum upvotes: 1000)
- r/coolguides (minimum upvotes: 500)
- r/lifehacks (minimum upvotes: 300)

### Agentic Coding
- r/ChatGPTCoding
- r/ClaudeAI
- r/CursorAI
- r/replit
- r/vibecoding
- r/ollama
- r/LocalLLaMA

### Technology & AI (currently disabled for Reddit section - these go to AI & Technology section)
- r/artificial
- r/LocalLLaMA
- r/OpenAI
- r/singularity
- r/MachineLearning

### Other
- r/bestof (minimum upvotes: 1000)
- r/InternetIsBeautiful (minimum upvotes: 500)

## Filtering Rules

- **Minimum upvote threshold**: Default 500 (override per subreddit above)
- **Minimum post age**: 6 hours (ensure upvotes have stabilized)
- **Maximum post age**: 48 hours (keep content fresh)
- **Maximum posts per subreddit**: 3 per day
- **Total Reddit highlights**: Maximum 8-10 items

## Content Filters

**Exclude posts containing these keywords:**
- "NSFW"
- "18+"
- Cryptocurrency price speculation
- Political flame wars

## Notes

- This file is checked each morning before generating the update
- To disable a subreddit, add "DISABLED" after its name
- Upvote thresholds help surface quality content
- Edit this file anytime to adjust your daily update preferences

---
*Last updated: 2025-09-26*
*Version: 0.3*