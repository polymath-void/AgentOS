import os
import json
import urllib.parse
import urllib.request
import logging
import time
from pathlib import Path

logger = logging.getLogger("github_client")

CLIENT_ID = "178c6fc778ccc68e1d6a"  # Public GitHub CLI Client ID
TOKEN_CACHE_FILE = Path(os.path.expanduser("~/.config/wc-cloud-repo-watch/github_token.txt"))

def do_browser_auth() -> str:
    """Initiates the GitHub OAuth Device Flow (Browser Auth)."""
    print("\n--- GitHub Browser Authentication ---")
    
    # 1. Request device code
    req = urllib.request.Request(
        "https://github.com/login/device/code",
        data=urllib.parse.urlencode({
            "client_id": CLIENT_ID,
            "scope": "repo workflow"
        }).encode("utf-8"),
        headers={"Accept": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        logger.error(f"Failed to start browser auth: {e}")
        return ""
        
    device_code = data["device_code"]
    user_code = data["user_code"]
    verification_uri = data["verification_uri"]
    interval = data["interval"]
    
    print(f"\n1. Open your browser and go to: {verification_uri}")
    print(f"2. Enter the following code: {user_code}\n")
    print("Waiting for authorization (this may take a moment)...")
    
    # 2. Poll for the access token
    token_url = "https://github.com/login/oauth/access_token"
    while True:
        time.sleep(interval)
        poll_req = urllib.request.Request(
            token_url,
            data=urllib.parse.urlencode({
                "client_id": CLIENT_ID,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
            }).encode("utf-8"),
            headers={"Accept": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(poll_req) as poll_res:
                poll_data = json.loads(poll_res.read().decode())
                
                if "access_token" in poll_data:
                    print("✅ Successfully authenticated!")
                    token = poll_data["access_token"]
                    
                    # Cache the token
                    TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
                    TOKEN_CACHE_FILE.write_text(token)
                    return token
                    
                if poll_data.get("error") == "authorization_pending":
                    continue
                if poll_data.get("error") == "slow_down":
                    interval += 5
                    continue
                if poll_data.get("error") == "expired_token":
                    print("❌ Code expired. Please try again.")
                    return ""
                    
        except urllib.error.URLError as e:
            logger.warning(f"Connection issue polling for token: {e}. Retrying in {interval}s...")
            continue
        except Exception as e:
            logger.error(f"Error polling for token: {e}")
            return ""

def get_github_token() -> str:
    """Retrieve the GitHub token from env, cache, or browser auth."""
    # 1. Try Environment Variable
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
        
    # 2. Try Cached File
    if TOKEN_CACHE_FILE.exists():
        return TOKEN_CACHE_FILE.read_text().strip()
        
    # 3. Fallback to Browser Auth (Device Flow)
    logger.info("No GITHUB_TOKEN found. Falling back to Browser Authentication.")
    return do_browser_auth()

def inject_auth_token(url: str) -> str:
    """
    Injects the GitHub PAT into the repository URL for authenticated git operations.
    e.g., https://github.com/user/repo.git -> https://x-access-token:<token>@github.com/user/repo.git
    """
    token = get_github_token()
    if not token or "x-access-token" in url or "@" in url:
        return url
        
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme in ["http", "https"] and "github.com" in parsed.netloc:
        new_netloc = f"x-access-token:{token}@{parsed.netloc}"
        new_url = parsed._replace(netloc=new_netloc).geturl()
        return new_url
        
    return url

def get_api_headers() -> dict:
    """Returns headers for GitHub API requests."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "wc-cloud-repo-watch"
    }
    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"
    return headers
