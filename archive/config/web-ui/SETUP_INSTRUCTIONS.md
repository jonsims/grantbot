# GitHub Personal Access Token Setup

To use the web config editor, you need a GitHub Personal Access Token (PAT) with permission to edit your repository.

## Step 1: Create a Personal Access Token

1. **Go to GitHub Settings**:
   - Visit: https://github.com/settings/tokens
   - Or: Click your profile → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Click "Generate new token"** → "Generate new token (classic)"

3. **Configure the token**:
   - **Note**: `Daily News Agent Config Editor`
   - **Expiration**: Choose `90 days` or `No expiration` (your choice)
   - **Select scopes**:
     - ✅ Check `repo` (Full control of private repositories)
       - This includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`

4. **Click "Generate token"** (green button at bottom)

5. **⚠️ IMPORTANT**: Copy the token immediately!
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - You won't be able to see it again
   - Save it somewhere safe (password manager recommended)

## Step 2: Use the Token in Web UI

1. **Open the config editor**:
   - Local: Open `config/web-ui/index.html` in your browser
   - GitHub Pages (after setup): `https://jonsims.github.io/daily-news-agent/config`

2. **Paste your token**:
   - Enter the token in the "GitHub Personal Access Token" field
   - Click "Save Token"
   - Token is stored in browser localStorage (this device only)

3. **Start editing!**:
   - The config will load automatically
   - Make your changes
   - Click "Save to GitHub" when done

## Step 3: Enable GitHub Pages (Optional)

To access the config editor from anywhere (not just locally):

1. **Go to your repo settings**:
   - https://github.com/jonsims/daily-news-agent/settings/pages

2. **Configure GitHub Pages**:
   - **Source**: Deploy from a branch
   - **Branch**: `v4-development`
   - **Folder**: `/config/web-ui`
   - Click "Save"

3. **Access from anywhere**:
   - URL: `https://jonsims.github.io/daily-news-agent/`
   - Or the URL GitHub provides in the Pages settings

## Security Notes

✅ **Safe practices**:
- Token is stored only in your browser's localStorage (device-specific)
- Token is never sent anywhere except GitHub API
- Use token expiration (90 days) for better security
- You can revoke the token anytime at: https://github.com/settings/tokens

⚠️ **Important**:
- Don't share your token with anyone
- Don't commit the token to git
- If you accidentally expose it, revoke it immediately and create a new one

## Troubleshooting

### "GitHub API error: 401"
- Your token is invalid or expired
- Create a new token and save it again

### "GitHub API error: 403"
- Token doesn't have `repo` scope
- Create a new token with proper permissions

### "GitHub API error: 404"
- Check that `GITHUB_OWNER` and `GITHUB_REPO` are correct in `config-editor.js`
- They should be: `jonsims` and `daily-news-agent`

### Config won't load
- Make sure you're on the `v4-development` branch
- Check that `config/sources-v4.yaml` exists in the repo

## Alternative: Fine-Grained Token (More Secure)

For better security, you can use a fine-grained token (beta):

1. **Go to**: https://github.com/settings/tokens?type=beta
2. **Click "Generate new token"**
3. **Configure**:
   - **Token name**: `Daily News Agent Config`
   - **Expiration**: 90 days
   - **Repository access**: Only select repositories → `daily-news-agent`
   - **Permissions**:
     - Repository permissions → Contents → Read and write
4. **Generate and copy token**

This limits the token to just this one repository!
