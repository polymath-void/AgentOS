import json
import subprocess
import logging
from pathlib import Path
from github_client import inject_auth_token

logger = logging.getLogger("cloud_poller")

def get_remote_sha(repo_url: str, branch: str = "main") -> str:
    auth_url = inject_auth_token(repo_url)
    try:
        result = subprocess.run(
            ["git", "ls-remote", auth_url, f"refs/heads/{branch}"],
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        if output:
            return output.split()[0]
        return ""
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking remote {repo_url}: {e.stderr}")
        return ""

def poll_fleet(fleet_data: dict, known_shas: dict) -> dict:
    changes_detected = {}
    repos = fleet_data.get("repositories", {})
    
    for repo_name, config in repos.items():
        url = config.get("url")
        branch = config.get("branch", "main")
        
        current_sha = get_remote_sha(url, branch)
        if current_sha:
            last_sha = known_shas.get(repo_name)
            if last_sha and last_sha != current_sha:
                changes_detected[repo_name] = current_sha
            known_shas[repo_name] = current_sha
            
    return changes_detected
