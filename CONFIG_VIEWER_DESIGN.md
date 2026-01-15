# Config Viewer - Current Design & Functionality

**File**: `config/web-ui/config-viewer.html`
**Purpose**: Read-only browser for RSS feed configuration
**Status**: Deployed to Cloudflare Pages

---

## Design Philosophy

**Inspiration**: GitHub's two-column interface
**Approach**: Clean, minimal, information-dense
**Technology**: Pure HTML/CSS/JavaScript (no frameworks)
**Color Scheme**: GitHub's design system

---

## Layout Structure

### Two-Column Layout

```
┌─────────────────────────────────────────────────────────┐
│  Header (Dark)                                          │
├──────────────┬──────────────────────────────────────────┤
│              │  Content Header (Category Title)          │
│  Sidebar     ├──────────────────────────────────────────┤
│  (280px)     │  Search Box                              │
│              ├──────────────────────────────────────────┤
│  Categories  │  Feed List                               │
│  List        │  - Feed 1 (with status dot)             │
│              │  - Feed 2 (with status dot)             │
│              │  - Feed 3 (disabled, grayed out)        │
│              ├──────────────────────────────────────────┤
│              │  Suggested Feeds Section                 │
│              │  - Suggestion 1                          │
│              │  - Suggestion 2                          │
└──────────────┴──────────────────────────────────────────┘
```

---

## Color Palette (GitHub-Inspired)

| Element | Color | Usage |
|---------|-------|-------|
| Header Background | `#24292f` | Dark header bar |
| Body Background | `#f6f8fa` | Light gray background |
| Primary Text | `#24292f` | Main text color |
| Secondary Text | `#57606a` | Metadata, labels |
| Links | `#0969da` | Blue links, buttons |
| Borders | `#d0d7de` | Subtle separators |
| Active Selection | `#ddf4ff` | Selected category highlight |
| Active Border | `#0969da` | 3px left border on active category |

---

## Components Breakdown

### 1. Header (Top Bar)
**Background**: Dark (`#24292f`)
**Contents**:
- Title: "⚙️ Configuration Viewer"
- Subtitle: "View RSS feeds and categories"
- Navigation links: Home, Email Archive, Feed Status

**Design**: Compact, matches GitHub's top navigation

---

### 2. Sidebar (Left Column)

#### Sidebar Header
- Title: "Categories"
- Compact stats: "21 categories • 104 feeds"
- Background: Light gray (`#f6f8fa`)

#### Category List
**Each category item**:
- Category name (14px, medium weight)
- Word target below name (12px, gray)
- Feed count badge (right-aligned, rounded pill)
- Hover effect: Light gray background
- **Active state**: Blue background + 3px left border

**Visual Hierarchy**:
```
┌──────────────────────────────┐
│ ai                        14 │  ← Active (blue bg)
│ 600 words                    │
├──────────────────────────────┤
│ academic_research          5 │  ← Hover state
│ 400 words                    │
├──────────────────────────────┤
│ moonshot_strategy         51 │  ← Default
│ 500 words                    │
└──────────────────────────────┘
```

---

### 3. Main Content (Right Panel)

#### Content Header
**Sticky header** that shows:
- Category name (18px, bold)
- Feed count + word target (13px, gray)
- Status legend with colored dots

**Status Legend**:
- Green ● = Working (has articles)
- Yellow ● = Empty (no articles)
- Red ● = Error (failed to fetch)
- Gray ● = Unknown (no status data)

#### Search Box
- Full-width input
- Placeholder: "Search feeds..."
- Filters feeds within selected category only
- Blue focus border (`#0969da`)

#### Feed List
**Each feed item**:

```
┌────────────────────────────────────────────────────────┐
│ ● OpenAI Blog                      🔗 Test Feed        │
│ https://openai.com/blog/rss                            │
│ [rss] [high]                                           │
└────────────────────────────────────────────────────────┘
```

**Components**:
- **Status dot** (8px circle) - colored based on feed health
- **Feed name** (14px, medium weight)
- **URL** (12px, monospace, blue link)
- **Badges** (11px pills):
  - Type badge (blue): "rss" or "reddit"
  - Priority badge (yellow): "high", "medium", "low"
- **Test Feed button** (blue, right-aligned)

**Disabled feeds**:
- 50% opacity
- "(disabled)" label after name
- All info still visible

---

### 4. Suggested Feeds Section

**Location**: Below feed list for each category
**Title**: "💡 Suggested Feeds (5)"

**Each suggestion card**:

```
┌────────────────────────────────────────────────────────┐
│ AI21 Labs Blog                      👁️ Preview  🔗 Test │
│ Jurassic AI model updates                              │
│ ~5-15 posts  [high quality]                            │
└────────────────────────────────────────────────────────┘
```

**Components**:
- **Name** (14px, medium weight)
- **Description** (12px, gray)
- **Metadata** (11px, gray):
  - Post frequency estimate
  - Quality badge (blue "high quality" or yellow "medium quality")
- **Actions**:
  - **Preview button** (white bg) - Opens blog/website
  - **Test Feed button** (blue bg) - Opens RSS feed

**Background**: Light gray box with white cards inside

---

## Functionality

### Data Loading

**On page load**:
1. Fetch `config/sources-v4.yaml` - Feed configuration
2. Fetch `config/feed-status.json` - Real-time feed health
3. Fetch `config/feed-suggestions.json` - Curated suggestions
4. Render sidebar categories
5. Show stats (category count, feed count)

### User Interactions

#### Category Selection
1. User clicks category in sidebar
2. Category highlights with blue background + left border
3. Right panel updates:
   - Shows category name and metadata
   - Displays status legend
   - Lists all feeds in category
   - Shows suggestions (if available)

#### Search
1. User types in search box
2. Filters feeds in **current category only**
3. Updates feed count in real-time
4. Shows "No feeds match" if empty

#### Feed Status
- **Hover over status dot**: Tooltip shows detailed status
  - "✓ 1 article fetched"
  - "⚠ No new articles (feed may be empty)"
  - "✗ Feed failed to load"

#### Testing Feeds
- **Test Feed button**: Opens RSS feed XML in new tab
  - User can verify feed works
  - See actual XML/RSS content
  - Check what articles are available

#### Preview Suggestions
- **Preview button** (suggestions only): Opens human-readable blog/website
  - NOT the XML feed
  - Actual blog homepage or section
  - User can browse before deciding to add

---

## Responsive Design

### Desktop (>768px)
- Two columns side-by-side
- Sidebar: 280px fixed width
- Main content: Flexible (fills remaining space)
- Height: `calc(100vh - 110px)` - both columns scroll independently

### Mobile (≤768px)
- Stacks vertically
- Sidebar becomes horizontal scrolling tabs
- Categories in horizontal row
- Full-width main content below

---

## Current Limitations

### Read-Only
**Cannot**:
- ❌ Add/remove feeds
- ❌ Enable/disable feeds
- ❌ Edit feed URLs or metadata
- ❌ Modify word targets
- ❌ Save changes

**Rationale**: Simple viewer focused on browsing/discovery

### Requires Separate Editor
For editing, user must use `config/web-ui/index.html`:
- Requires GitHub authentication
- Can modify YAML config
- Can save changes via GitHub API
- More complex interface

---

## Performance

### Load Time
- Initial load: ~200-500ms
- Config parsing: ~50ms
- Rendering: ~100ms

### Data Size
- `sources-v4.yaml`: ~15KB
- `feed-status.json`: ~20KB
- `feed-suggestions.json`: ~10KB
- **Total**: ~45KB (very fast)

### Caching
- Browser caches all JSON/YAML files
- Cloudflare CDN edge caching
- No authentication = no dynamic data

---

## User Experience Flow

### First Visit
1. Page loads → Shows categories in sidebar
2. Empty state in main panel: "Select a category to view its feeds"
3. User clicks category (e.g., "ai")
4. Feeds load with status indicators
5. Suggestions appear at bottom

### Browsing
1. User scrolls through feeds, sees status dots
2. Hovers over dots to see detailed status
3. Clicks "Test Feed" to verify RSS works
4. Sees grayed-out disabled feeds
5. Scrolls to suggestions section
6. Clicks "Preview" to view blog sites
7. Clicks "Test Feed" on suggestions to verify before adding

### Searching
1. User types "reddit" in search
2. Feed list filters to show only reddit feeds
3. Feed count updates: "14 feeds" → "7 feeds"
4. Clear search to see all again

---

## Future Enhancement Ideas

*(User will edit this section)*

### Potential Improvements
-
-
-

### Missing Features
-
-
-

### UX Refinements
-
-
-

### Design Changes
-
-
-

---

## Technical Details

### File Structure
```
config/web-ui/config-viewer.html
├── HTML Structure
│   ├── Header (navigation)
│   ├── Sidebar (categories)
│   └── Main Content (feeds)
├── CSS (<style> tag)
│   ├── Layout (flexbox)
│   ├── Colors (GitHub palette)
│   └── Components (cards, badges, buttons)
└── JavaScript (<script> tag)
    ├── Data loading (fetch APIs)
    ├── YAML parsing (simple regex)
    ├── Rendering (template strings)
    └── Event handlers (click, search)
```

### Dependencies
**None!** Pure vanilla JS, no libraries.

### Browser Support
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive

---

## Deployment

### Hosting
- **Platform**: Cloudflare Pages
- **URL**: https://daily-news-agent.pages.dev/config/web-ui/config-viewer.html
- **Branch**: `v4-development`
- **Auto-deploy**: Every push (~30 seconds)

### Access
- **Public** (but authenticated via Cloudflare Access)
- **No GitHub auth required** (read-only)
- **Fast** (edge-cached globally)

---

## Comparison: Config Viewer vs Config Editor

| Feature | Config Viewer | Config Editor |
|---------|--------------|---------------|
| **Purpose** | Browse feeds | Edit feeds |
| **Authentication** | Cloudflare Access | GitHub token |
| **Can View Feeds** | ✅ Yes | ✅ Yes |
| **Can Edit Feeds** | ❌ No | ✅ Yes |
| **Can Add Feeds** | ❌ No | ✅ Yes |
| **Can Disable Feeds** | ❌ No (shows only) | ✅ Yes |
| **Feed Suggestions** | ✅ Yes | ✅ Yes |
| **Feed Status** | ✅ Yes | ✅ Yes |
| **Test Feed Links** | ✅ Yes | ✅ Yes |
| **Design** | GitHub-style, clean | Form-based, dense |
| **Use Case** | Quick browsing | Configuration management |

---

## Notes for Next Version

*(User will add ideas here)*

**Design improvements to consider**:
-
-
-

**Functionality to add**:
-
-
-

**User feedback**:
-
-
-

---

*Last updated: 2025-10-11*
*Created with Claude Code*
