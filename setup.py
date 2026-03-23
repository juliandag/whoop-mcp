#!/usr/bin/env python3
"""
WHOOP MCP Server Setup Script
Direct OAuth authorization (no proxy needed)
"""
import os
import sys
import webbrowser
import requests
import json
import secrets
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
from threading import Thread

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.auth_manager import TokenManager
from src.config import (
    OAUTH_AUTH_URL, OAUTH_TOKEN_URL,
    WHOOP_CLIENT_ID, WHOOP_CLIENT_SECRET, WHOOP_REDIRECT_URI, WHOOP_SCOPES
)


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color=Colors.ENDC):
    print(f"{color}{text}{Colors.ENDC}")


# Global to capture the auth code from the callback
captured_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth callback"""

    def do_GET(self):
        global captured_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if 'code' in params:
            captured_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Success!</h1>'
                             b'<p>Authorization complete. You can close this tab and return to the terminal.</p>'
                             b'</body></html>')
        else:
            error = params.get('error', ['unknown'])[0]
            self.send_response(400)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(f'<html><body><h1>Error</h1><p>{error}</p></body></html>'.encode())

    def log_message(self, format, *args):
        pass  # Suppress request logs


def main():
    global captured_code

    print_colored("=" * 60, Colors.HEADER)
    print_colored("WHOOP MCP Server Setup (Direct OAuth)", Colors.HEADER)
    print_colored("=" * 60, Colors.HEADER)
    print()

    if not WHOOP_CLIENT_ID or not WHOOP_CLIENT_SECRET:
        print_colored("Error: WHOOP_CLIENT_ID and WHOOP_CLIENT_SECRET must be set in .env", Colors.FAIL)
        sys.exit(1)

    # Build authorization URL
    state = secrets.token_urlsafe(32)
    auth_params = {
        'client_id': WHOOP_CLIENT_ID,
        'redirect_uri': WHOOP_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(WHOOP_SCOPES),
        'state': state,
    }
    auth_url = f"{OAUTH_AUTH_URL}?{urllib.parse.urlencode(auth_params)}"

    # Start local callback server
    parsed_redirect = urllib.parse.urlparse(WHOOP_REDIRECT_URI)
    port = parsed_redirect.port or 8080

    server = HTTPServer(('localhost', port), CallbackHandler)
    server_thread = Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print_colored(f"Listening on localhost:{port} for callback...", Colors.OKBLUE)
    print_colored("Opening browser for WHOOP authorization...", Colors.OKBLUE)
    print()

    webbrowser.open(auth_url)

    print_colored("Waiting for authorization (complete it in your browser)...", Colors.WARNING)
    server_thread.join(timeout=120)
    server.server_close()

    if not captured_code:
        print_colored("Timed out or no authorization code received.", Colors.FAIL)
        sys.exit(1)

    print_colored("Authorization code received!", Colors.OKGREEN)

    # Exchange code for tokens
    print_colored("Exchanging code for tokens...", Colors.OKBLUE)

    response = requests.post(
        OAUTH_TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'code': captured_code,
            'client_id': WHOOP_CLIENT_ID,
            'client_secret': WHOOP_CLIENT_SECRET,
            'redirect_uri': WHOOP_REDIRECT_URI,
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30,
    )

    if response.status_code != 200:
        print_colored(f"Token exchange failed ({response.status_code}): {response.text}", Colors.FAIL)
        sys.exit(1)

    token_data = response.json()
    print_colored("Tokens received!", Colors.OKGREEN)

    # Save tokens
    token_manager = TokenManager()
    token_manager.save_tokens(token_data)
    print_colored("Tokens saved securely.", Colors.OKGREEN)

    # Verify
    token_info = token_manager.get_token_info()
    print()
    print_colored(f"  Status:        {token_info['status']}", Colors.OKBLUE)
    print_colored(f"  Expires at:    {token_info['expires_at']}", Colors.OKBLUE)
    print_colored(f"  Refresh token: {token_info['has_refresh_token']}", Colors.OKBLUE)
    print()
    print_colored("Setup complete! Restart Claude Desktop to use the WHOOP MCP server.", Colors.OKGREEN)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nSetup interrupted.", Colors.WARNING)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\nError: {e}", Colors.FAIL)
        sys.exit(1)
