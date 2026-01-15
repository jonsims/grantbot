# ✅ MILESTONE 2: HTML Config Interface - TESTING GUIDE

## What Was Built

**Simple HTML config interface** to manage RSS feeds and categories from your browser.

### Key Features:
- **Toggle feeds on/off** with checkboxes
- **Adjust word targets** per category (number inputs)
- **Add new RSS feeds** with simple form
- **Save to GitHub** via API (no command line needed!)
- **Works from any device** (when GitHub Pages is enabled)

---

## 🧪 Testing Milestone 2

### Test 1: Setup GitHub Personal Access Token (One-Time)

Follow the setup instructions:

1. **Open**: [config/web-ui/SETUP_INSTRUCTIONS.md](config/web-ui/SETUP_INSTRUCTIONS.md)
2. **Follow Steps 1-2** to create and save your GitHub token
3. **Expected**: Token saved confirmation message

**Quick Link**: https://github.com/settings/tokens

**Scopes needed**: ✅ `repo` (Full control of private repositories)

### Test 2: Open Config Editor Locally

```bash
# From the repo directory
open config/web-ui/index.html
```

Or manually:
1. Open Finder
2. Navigate to `config/web-ui/`
3. Double-click `index.html`

**Expected**: Config editor opens in your default browser

### Test 3: Load Configuration

1. **Paste your GitHub token** in the auth section
2. **Click "Save Token"**
3. **Expected**:
   - "Token saved! Loading configuration..." message
   - Config loads with all categories visible
   - Each category shows:
     - Category name (e.g., "AI Technology")
     - Word target number input
     - List of sources with checkboxes
     - "Add Source" button

### Test 4: Toggle a Feed On/Off

1. **Find a source** (e.g., "GitHub Blog" in AI category)
2. **Uncheck the checkbox**
3. **Click "Save to GitHub"**
4. **Confirm the save prompt**
5. **Expected**: "✅ Configuration saved to GitHub successfully!"

**Verify it worked**:
```bash
cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent"
git pull
grep "GitHub Blog" config/sources-v4.yaml
```

The source should be removed from the YAML file!

### Test 5: Adjust Word Target

1. **Find "AI Technology" category**
2. **Change word target** from 600 to 700
3. **Click "Save to GitHub"**
4. **Expected**: Save confirmation

**Verify**:
```bash
grep -A 2 "ai:" config/sources-v4.yaml
```

Should show `word_target: 700`

### Test 6: Add a New RSS Feed

1. **Click "+ Add Source"** in any category
2. **Fill in the form**:
   - Name: `Test Blog`
   - URL: `https://example.com/feed.xml`
3. **Click "Add"**
4. **Expected**: New source appears in the list
5. **Click "Save to GitHub"**

**Verify**:
```bash
grep "Test Blog" config/sources-v4.yaml
```

### Test 7: Download Backup

1. **Click "Download Backup"** button
2. **Expected**: YAML file downloads with name like:
   - `sources-v4-backup-2025-10-10.yaml`
3. **Open the file**: Should contain your current config

### Test 8: Reload Config

1. **Make a change** (don't save)
2. **Click "Reload Config"**
3. **Expected**: Change is discarded, original config restored

---

## ✅ Success Criteria

**Milestone 2 is successful if:**

1. ✅ Config editor loads in browser
2. ✅ GitHub token can be saved and persists
3. ✅ Configuration loads from GitHub
4. ✅ Can toggle feeds on/off
5. ✅ Can adjust word targets
6. ✅ Can add new RSS feeds
7. ✅ Changes save to GitHub successfully
8. ✅ Changes appear in `config/sources-v4.yaml` after save

---

## 🐛 Troubleshooting

### Issue: "GitHub API error: 401"

**Solution**: Token is invalid/expired
- Create new token at: https://github.com/settings/tokens
- Make sure to select `repo` scope
- Copy and save the new token

### Issue: "GitHub API error: 403"

**Solution**: Token doesn't have correct permissions
- Token must have `repo` scope (not just `public_repo`)
- Create a new token with full `repo` access

### Issue: Config won't load

**Checklist**:
1. Is your token saved? (check localStorage in browser dev tools)
2. Is the repo name correct in `config-editor.js`?
   - Should be: `GITHUB_OWNER = 'jonsims'`
   - Should be: `GITHUB_REPO = 'daily-news-agent'`
3. Are you on `v4-development` branch?
4. Does `config/sources-v4.yaml` exist?

### Issue: Changes not appearing after save

**Solution**: Pull latest changes from GitHub
```bash
cd "/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/daily-news-agent"
git pull origin v4-development
```

### Issue: Browser shows "file://" URL restrictions

**Solution**: This is expected for local files. Two options:
1. **Use local Python server**:
   ```bash
   cd config/web-ui
   python3 -m http.server 8000
   # Open http://localhost:8000 in browser
   ```
2. **Enable GitHub Pages** (see SETUP_INSTRUCTIONS.md Step 3)

---

## 📱 Optional: Enable GitHub Pages (Access from Phone)

Want to edit config from your phone or any device?

1. **Go to repo settings**: https://github.com/jonsims/daily-news-agent/settings/pages
2. **Set source**: `v4-development` branch, `/config/web-ui` folder
3. **Wait 1-2 minutes** for deployment
4. **Access at**: `https://jonsims.github.io/daily-news-agent/`

Now you can edit config from anywhere! 📱💻

---

## 🔒 Security Notes

- ✅ Token stored in browser localStorage only (never sent anywhere except GitHub)
- ✅ Token is device-specific (won't sync to other devices)
- ✅ You can revoke token anytime: https://github.com/settings/tokens
- ✅ Recommended: Use 90-day expiration for better security

---

## 🎯 Next Steps After Testing

Once you've verified Milestone 2 works:

1. **Test on your phone** (if GitHub Pages is enabled)
2. **Customize some feeds** to your preferences
3. **Let me know if you need any changes** (e.g., different layout, more features)
4. **We'll proceed to Milestone 3**: RSS Feed Generation

---

## 📁 Files Created

- `config/web-ui/index.html` - Main interface
- `config/web-ui/config-editor.js` - JavaScript logic
- `config/web-ui/SETUP_INSTRUCTIONS.md` - Token setup guide
- `V4_MILESTONE_2_TEST.md` - This testing guide
