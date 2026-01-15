# Daily News Agent - Automation Setup

## API Keys Configuration

Both API keys are stored in `.env` file:

```
OPENAI_API_KEY=sk-proj-your-openai-key-here

CLAUDE_API_KEY=sk-ant-your-anthropic-key-here
```

**API Fallback Order**: Claude → OpenAI → Mock (empty)

The system will automatically try Claude first, then fall back to OpenAI if Claude fails or is unavailable.

---

## Installing the 4am Daily Schedule

To set up automatic daily updates at 4:00 AM:

### 1. Copy LaunchAgent to system location

```bash
cp com.jonsims.dailynewsagent.plist ~/Library/LaunchAgents/
```

### 2. Load the LaunchAgent

```bash
launchctl load ~/Library/LaunchAgents/com.jonsims.dailynewsagent.plist
```

### 3. Verify it's running

```bash
launchctl list | grep dailynewsagent
```

## Managing the Schedule

### Check status
```bash
launchctl list com.jonsims.dailynewsagent
```

### Stop the schedule
```bash
launchctl unload ~/Library/LaunchAgents/com.jonsims.dailynewsagent.plist
```

### Restart after changes
```bash
launchctl unload ~/Library/LaunchAgents/com.jonsims.dailynewsagent.plist
cp com.jonsims.dailynewsagent.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jonsims.dailynewsagent.plist
```

### Test manual run
```bash
./run_daily_update.sh
```

Or for test mode:
```bash
python3 src/main_v2.py --test
```

## Logs

- Execution logs: `logs/automation.log`
- Standard output: `logs/stdout.log`
- Errors: `logs/stderr.log`

## Current Configuration

- **Schedule**: Daily at 4:00 AM
- **Mode**: Production (no "Test" prefix)
- **Output**: `/Users/jonsims/Documents/Obsidian Vault/Daily Updates (Agent)/Published Updates/`
- **Email**: Automatically sent if configured in `.env`

## Troubleshooting

If the automation doesn't run:

1. Check logs in `logs/` directory
2. Verify script permissions: `ls -l run_daily_update.sh` (should be executable)
3. Test manual run: `./run_daily_update.sh`
4. Check LaunchAgent status: `launchctl list com.jonsims.dailynewsagent`

---
*Version: 0.3*