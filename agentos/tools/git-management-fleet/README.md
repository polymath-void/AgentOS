# github-cli-management-and-repo_watcher

A Cloud Git Repository Fleet Management tool (`wc-cloud-repo-watch`) designed to monitor, auto-reconcile, and self-heal a fleet of GitHub repositories autonomously using Swarm Agent logic.

## Features
- **Cloud Poller**: Tracks branch divergence across a JSON-configured fleet using `git ls-remote`.
- **Cascade Engine**: Automatically propagates dependency updates to downstream repos.
- **Auto Reconcile**: Fetches and rebases divergent branches automatically.
- **Self Healing**: Monitors GitHub Actions and patches failing tests via AI traceback analysis.
- **Native Browser Auth**: Includes GitHub Device Flow for seamless authentication.

## Installation & Usage
```bash
# Clone the repository
git clone https://github.com/polymath-void/github-cli-management-and-repo_watcher.git
cd github-cli-management-and-repo_watcher

# Run the watcher daemon (polls every 60s)
python3 bin/wc-cloud-repo-watch --watch --interval 60

# Check status matrix
python3 bin/wc-cloud-repo-watch --status
```
