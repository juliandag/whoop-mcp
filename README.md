# WHOOP MCP Server

> Connect your WHOOP fitness data to Claude Desktop through the Model Context Protocol (MCP)

Access your workouts, recovery, sleep patterns, and more through natural language queries in Claude Desktop — all data stays local and private.

## Setup

### Prerequisites
- Python 3.10+
- Claude Desktop
- Active WHOOP account
- A WHOOP Developer App ([create one here](https://developer-dashboard.whoop.com/apps/create))

### 1. Create a WHOOP Developer App

1. Go to https://developer-dashboard.whoop.com
2. Create a team (if prompted)
3. Create a new app with these settings:
   - **Scopes:** `read:profile`, `read:workout`, `read:sleep`, `read:recovery`, `read:cycles`, `offline`
   - **Redirect URI:** `http://localhost:8080/callback`
4. Note your **Client ID** and **Client Secret**

### 2. Install

```bash
git clone https://github.com/juliandag/whoop-mcp.git
cd whoop-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your Client ID and Client Secret from step 1.

### 4. Authenticate

```bash
source .venv/bin/activate
python setup.py
```

This opens your browser for WHOOP login. After authorizing, tokens are saved locally and encrypted.

### 5. Configure Claude Desktop

Add to your Claude Desktop config:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "whoop": {
      "command": "/path/to/whoop-mcp/.venv/bin/python",
      "args": ["/path/to/whoop-mcp/src/whoop_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/whoop-mcp/src"
      }
    }
  }
}
```

Replace `/path/to/whoop-mcp` with the actual path where you cloned the repo.

### 6. Restart Claude Desktop

## Usage

Once configured, ask Claude things like:

- "Show my WHOOP profile"
- "What were my workouts this week?"
- "How is my recovery trending?"
- "Show my sleep data for the last 7 days"
- "What's my HRV looking like?"

## Available Tools

| Tool | Description |
|------|-------------|
| `get_whoop_profile` | User profile info |
| `get_whoop_workouts` | Workout data (filterable by date/limit) |
| `get_whoop_recovery` | Recovery scores (filterable by date/limit) |
| `get_whoop_sleep` | Sleep data (filterable by date/limit) |
| `get_whoop_cycles` | Daily physiological cycles (filterable by date/limit) |
| `get_whoop_auth_status` | Check auth status |
| `clear_whoop_cache` | Clear cached API responses |

## Security

- Tokens are encrypted at rest (AES)
- All data stored locally, never sent to third parties
- Token files have restricted permissions (600)
- Automatic token refresh

## Troubleshooting

**"No valid access token available"** — Re-run `python setup.py`

**Claude Desktop doesn't see the server** — Use full absolute paths in the config and run `which python3` to find the correct Python path. Restart Claude Desktop after changes.

**"Rate limit exceeded"** — Wait a minute before making more requests.

## License

MIT

## Disclaimer

Unofficial integration using the official WHOOP API. Not endorsed by WHOOP.

Based on [RomanEvstigneev/whoop-mcp-server](https://github.com/RomanEvstigneev/whoop-mcp-server), modified for direct OAuth (no proxy dependency).
