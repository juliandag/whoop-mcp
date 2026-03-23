"""
Configuration for WHOOP MCP Server
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# OAuth credentials (from .env)
WHOOP_CLIENT_ID = os.getenv('WHOOP_CLIENT_ID', '')
WHOOP_CLIENT_SECRET = os.getenv('WHOOP_CLIENT_SECRET', '')
WHOOP_REDIRECT_URI = os.getenv('WHOOP_REDIRECT_URI', 'http://localhost:8080/callback')

# WHOOP OAuth endpoints (direct)
OAUTH_AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
OAUTH_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"

# WHOOP API configuration
WHOOP_API_BASE = "https://api.prod.whoop.com/developer/v1"
WHOOP_SCOPES = [
    "read:profile",
    "read:workout",
    "read:sleep",
    "read:recovery",
    "offline"
]

OAUTH_REFRESH_URL = OAUTH_TOKEN_URL  # Same endpoint for refresh

# Storage configuration
import os
HOME_DIR = os.path.expanduser("~")
STORAGE_DIR = os.path.join(HOME_DIR, ".whoop-mcp-server")
TOKEN_STORAGE_PATH = os.path.join(STORAGE_DIR, "tokens.json")
CACHE_STORAGE_PATH = os.path.join(STORAGE_DIR, "cache.json")
CACHE_DURATION = 300  # 5 minutes

# Security configuration
ENCRYPTION_KEY_FILE = os.path.join(STORAGE_DIR, ".encryption_key")

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 100
REQUEST_TIMEOUT = 30  # seconds

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', None)  # None means console only