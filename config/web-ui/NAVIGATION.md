# Web UI Navigation Map

## Current Active Pages

### 1. Homepage (`/index.html`)
**URL**: http://localhost:8000/index.html
**Live**: https://daily-news-agent.pages.dev/

**Links to:**
- ⚙️ Feed Manager → `/config/web-ui/config-unified.html`
- 📧 Email Archive → `/config/web-ui/email-archive.html`

---

### 2. Feed Manager (`/config/web-ui/config-unified.html`)
**URL**: http://localhost:8000/config/web-ui/config-unified.html
**Live**: https://daily-news-agent.pages.dev/config/web-ui/config-unified.html

**Features:**
- Sidebar navigation with all feed categories
- Dashboard view with feed health statistics
- Per-category feed management
- Feed suggestions
- Search and filter
- Toggle feeds on/off
- Bulk actions (Enable All, Disable All, Disable Empty, Disable Errors)

**Links to:**
- 🏠 Back to Home → `/index.html`
- 📧 Email Archive → `email-archive.html`

---

### 3. Email Archive (`/config/web-ui/email-archive.html`)
**URL**: http://localhost:8000/config/web-ui/email-archive.html
**Live**: https://daily-news-agent.pages.dev/config/web-ui/email-archive.html

**Features:**
- Sidebar navigation with emails grouped by month
- Filter by version (All, v2, v4)
- Click to view email in iframe
- "Open in New Tab" link for full-screen viewing

**Links to:**
- 🏠 Back to Home → `../../index.html`
- ⚙️ Feed Manager → `config-unified.html`

---

## Navigation Flow

```
Homepage (index.html)
    ├─→ Feed Manager (config-unified.html)
    │       ├─→ Back to Home
    │       └─→ Email Archive
    │
    └─→ Email Archive (email-archive.html)
            ├─→ Back to Home
            └─→ Feed Manager
```

All pages form a complete navigation circle - you can reach any page from any other page.

---

## Archived Pages

Obsolete files moved to `/config/web-ui/archive/`:
- `config-viewer.html` (replaced by config-unified.html)
- `feed-status.html` (integrated into config-unified.html Dashboard)
- `index.html` (old config editor, replaced by config-unified.html)
- `design-mockups.html` (design exploration)
- `sidebar-mockup.html` (implemented in config-unified.html)
- `config-unified-backup.html` (backup before adding suggestions)

See `/config/web-ui/archive/README.md` for details.

---

## Design Consistency

All active pages share:
- **Color scheme**: Teal/green (#0d9488, #0f766e, #14b8a6)
- **Layout**: Fixed sidebar (280px) + main content area
- **Typography**: -apple-system, BlinkMacSystemFont, 'Segoe UI'
- **Components**: Sidebar header with gradient, navigation items, footer with links
- **Buttons**: Consistent styling with hover states
- **Status indicators**: Green (success), Yellow (empty), Red (error)

---

## Local Testing

Start HTTP server:
```bash
cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent"
python3 -m http.server 8000
```

Then visit:
- http://localhost:8000/index.html
- http://localhost:8000/config/web-ui/config-unified.html
- http://localhost:8000/config/web-ui/email-archive.html

---

## Cloudflare Deployment

All pages auto-deploy to Cloudflare Pages on push to `v4-development` branch:
- https://daily-news-agent.pages.dev/
- https://daily-news-agent.pages.dev/config/web-ui/config-unified.html
- https://daily-news-agent.pages.dev/config/web-ui/email-archive.html

Deploy time: ~30 seconds after push.
