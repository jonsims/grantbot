# GrantBot PRD
**Version:** 1.0
**Date:** January 15, 2026
**Authors:** Jon, Erik

---

## Overview

GrantBot is an agentic tool that discovers grant opportunities and analyzes them for fit with Generator AI Lab. It runs daily (automated) or on-demand, delivering actionable intelligence about funding opportunities.

---

## Problem

Finding grants is tedious:
- Scattered across dozens of sources (grants.gov, NSF, foundations, state agencies)
- Most aren't relevant to our focus areas
- Evaluating fit takes significant time per grant
- Easy to miss deadlines or opportunities

---

## Solution

An AI-powered agent that:
1. **Collects** grant listings from multiple sources
2. **Filters** for relevance to our org profile
3. **Analyzes** each match in depth
4. **Delivers** a prioritized digest with actionable next steps

---

## Organization Profile

**Entity:** Generator AI Lab at Babson College
**Type:** University/College
**Location:** Massachusetts
**Focus Areas:**
- Entrepreneurship
- Innovation
- AI impact
- Pedagogical research (interdisciplinary)

**Grant Sizes:** All ($1K to $1M+)

**Key Foundations:**
- Kauffman Foundation (entrepreneurship)
- Others TBD (GrantBot will identify)

---

## Features

### 1. Grant Collection
Pull opportunities from:
- grants.gov (federal)
- NSF (National Science Foundation)
- Foundation directories
- State/regional agencies
- RSS feeds from relevant sources

### 2. Smart Filtering
Match grants against org profile:
- Eligibility (university, nonprofit, etc.)
- Focus area alignment
- Geographic restrictions
- Grant size range

### 3. Full Analysis (per match)
For each relevant grant, provide:

| Analysis Component | Description |
|-------------------|-------------|
| **Summary** | What the grant funds, who's offering it |
| **Fit Score** | How well it matches our focus areas (1-10) |
| **Eligibility Check** | Confirm we qualify |
| **Budget Fit** | Grant size vs. typical project costs |
| **Competition Level** | Estimated competitiveness (if available) |
| **Strategic Fit** | How this aligns with lab goals |
| **Action Items** | Deadline, application link, key contacts |

### 4. Delivery

**Daily Email Digest**
- Scheduled delivery (morning)
- Prioritized list of new opportunities
- Quick-scan format with full analysis linked

**On-Demand**
- Run manually anytime
- Immediate results in terminal or local file
- Same analysis depth as email

---

## Technical Approach

Fork of daily-news-agent v5, adapting:

| Component | Daily News | GrantBot |
|-----------|-----------|----------|
| Collectors | RSS feeds, Readwise | grants.gov API, NSF, foundation RSS |
| Processors | News summarization | Grant matching + analysis |
| Config | `sources.yaml` | `sources-grants.yaml` + `org-profile.yaml` |
| Output | News digest | Grant analysis digest |

---

## Data Sources (Initial)

1. **grants.gov** - Federal grants API
2. **NSF** - RSS feeds (programs TBD based on focus areas)
3. **Kauffman Foundation** - Entrepreneurship grants
4. **Other foundations** - To be identified based on focus areas
5. **Massachusetts state grants** - MassTech, Mass Life Sciences, etc.

---

## Success Criteria

- [ ] Discovers grants we wouldn't have found manually
- [ ] Analysis is accurate enough to trust (eligibility, deadlines)
- [ ] Saves time vs. manual searching
- [ ] Zero missed deadlines for grants we're pursuing

---

## Users

- Jon
- Erik

(2-person team, no multi-tenant requirements)

---

## Milestones

### M1: Foundation
- [ ] Org profile config (`org-profile.yaml`)
- [ ] grants.gov collector working
- [ ] Basic matching (keyword + eligibility)

### M2: Analysis
- [ ] Full analysis pipeline
- [ ] Fit scoring
- [ ] Action items extraction

### M3: Delivery
- [ ] Email digest working
- [ ] On-demand CLI mode
- [ ] Daily automation (GitHub Actions or local cron)

### M4: Expansion
- [ ] Add NSF, foundation sources
- [ ] Refine matching based on results
- [ ] Historical tracking (what we applied for, outcomes)

---

## Answered Questions

1. **NSF programs:** GrantBot should identify relevant programs based on org profile (entrepreneurship, innovation, AI, pedagogy)
2. **Foundations:** Kauffman Foundation (entrepreneurship focus) + others to be identified
3. **State grants:** Massachusetts (Babson College location)
4. **Deadline horizon:** No limit - surface all opportunities regardless of deadline

---

## Appendix A: Potential Tools & Libraries

GitHub repos that may accelerate development:

### AI Grant Matching
| Repo | Description |
|------|-------------|
| [vanderbilt-data-science/grant-match](https://github.com/vanderbilt-data-science/grant-match) | AI-powered matching with reasoning explanations. **Closest to our use case.** |
| [CrewAI Grant Finder](https://github.com/deacs11/CrewAI_Grant_Funding_Opportunity_Finder_-_Eligibility_Checker_Crew) | Multi-agent system (CrewAI) for eligibility checking and report generation |

### Federal Grants Collection
| Repo | Description |
|------|-------------|
| [HHS/simpler-grants-gov](https://github.com/HHS/simpler-grants-gov) | Official HHS grants.gov modernization (Python/Flask) |
| [ericmuckley/foa-finder](https://github.com/ericmuckley/foa-finder) | Automated grants.gov scraper (daily XML exports) |
| [DanNBullock/USG_grants_crawl](https://github.com/DanNBullock/USG_grants_crawl) | Multi-source federal crawler (grants.gov, NIH, NSF, DOE) |

### NSF Specific
| Repo | Description |
|------|-------------|
| [samapriya/nsfsearch](https://github.com/samapriya/nsfsearch) | CLI for NSF Awards API with CSV export |
| [titipata/grant_database](https://github.com/titipata/grant_database) | NIH + NSF parser with deduplication |
| [m-nolan/NSF-grant-award-scraper](https://github.com/m-nolan/NSF-grant-award-scraper) | NSF award database scraper (1959-present) |

### Foundation Data
| Repo | Description |
|------|-------------|
| [grantmakers.io](https://github.com/grantmakers) | Open source IRS 990-PF search (3.3M foundation grants) |
| [EMKF/Indicators-KauffmanEarlyStageEntrepreneurship](https://github.com/EMKF/Indicators-KauffmanEarlyStageEntrepreneurship) | Kauffman Foundation data/indicators |

### AI Grant Writing
| Repo | Description |
|------|-------------|
| [eseckel/ai-for-grant-writing](https://github.com/eseckel/ai-for-grant-writing) | Curated LLM resources for grant applications |
| [UABPeriopAI/Grant_Guide](https://github.com/UABPeriopAI/Grant_Guide) | NIH grant drafting with NIH-RePORTER integration |
| [zaina-saif/GrantAIScraper](https://github.com/zaina-saif/GrantAIScraper) | Streamlit + LangChain scraper for nonprofits |

### Recommended Starting Points
- **grants.gov collector**: foa-finder or simpler-grants-gov
- **NSF collector**: nsfsearch
- **AI matching logic**: grant-match (Vanderbilt)
- **Foundation data**: grantmakers.io

---

## Appendix B: Existing Architecture

From daily-news-agent:
```
src/
├── collectors/      # Data fetching (adapt for grants)
├── processors/      # AI summarization (adapt for analysis)
├── generators/      # Output formatting
└── utils/           # Email, caching, etc.

config/
├── sources-v5.yaml  # News sources (replace with grants)
└── templates/       # Output templates
```
