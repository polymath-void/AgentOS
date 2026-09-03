# 📦 Git Setup & Deployment Guide — SaaS-Agent v2

**Complete steps to initialize git, commit, and push to GitHub for production management.**

---

## Step 1: Choose Your GitHub Repo

### Option A: New Repository (Recommended)

```bash
# On GitHub, create a new repo:
# - Name: saas-agent-v2
# - Visibility: Private or Public
# - Do NOT initialize with README (we have one)
# Copy the HTTPS or SSH URL
```

### Option B: Existing Repository

If you have an existing repo where you want to add this project as a subtree or complete replacement, use that URL instead.

---

## Step 2: Initialize Git in the Project

Navigate to the downloaded project:

```bash
cd /path/to/saas-agent-v2  # or wherever you extracted the files
```

Initialize git:

```bash
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files (respects .gitignore)
git add .

# Create initial commit
git commit -m "🚀 Initial commit: SaaS-Agent v2 — Deterministic execution-based personal OS agent"

# Verify
git log --oneline
git status
```

---

## Step 3: Add Remote & Push

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub details:

### HTTPS (Recommended for start)

```bash
git remote add origin https://github.com/YOUR_USERNAME/saas-agent-v2.git
git branch -M main
git push -u origin main
```

### SSH (If you have SSH keys set up)

```bash
git remote add origin git@github.com:YOUR_USERNAME/saas-agent-v2.git
git branch -M main
git push -u origin main
```

**Output should show:**
```
Enumerating objects: 25, done.
Counting objects: 100% (25/25), done.
Delta compression using up to 8 threads
...
To github.com:YOUR_USERNAME/saas-agent-v2.git
 * [new branch]      main -> main
Branch 'main' is set up to track remote branch 'main' from 'origin'.
```

---

## Step 4: Verify on GitHub

1. Go to `https://github.com/YOUR_USERNAME/saas-agent-v2`
2. You should see all files:
   - `main.py`, `models.py`, etc.
   - `static/app.html`, `manifest.json`, `sw.js`
   - `.github/workflows/test.yml` (CI/CD)
   - `README_PRODUCTION.md`

3. **GitHub Actions should auto-run** the test workflow (check the Actions tab)

---

## Step 5: Configure Secrets for CI/CD (Optional)

If you want GitHub Actions to test with real Gemini API:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add:
   - Name: `GEMINI_API_KEY`
   - Value: `your-actual-api-key`

4. Update `.github/workflows/test.yml` to use it:

```yaml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

---

## Step 6: Ongoing Workflow

### Make Changes Locally

```bash
# Edit a file (e.g., add new tool)
nano tool_registry.py

# Stage changes
git add tool_registry.py

# Commit with clear message
git commit -m "feat: add weather API tool"

# Push to GitHub
git push origin main
```

### Create a Feature Branch (Best Practice)

```bash
# Create feature branch
git checkout -b feature/add-weather-tool

# Make changes
git add .
git commit -m "feat: integrate weather API with system monitoring"

# Push branch
git push origin feature/add-weather-tool

# On GitHub, create a Pull Request → review → merge to main
```

### Merge Strategy

```
main (production)
  ↑ (PRs merged here)
  └─ develop (staging)
      ↑ (feature branches)
      └─ feature/name-1, feature/name-2, etc.
```

Setup:

```bash
# Create develop branch
git checkout -b develop
git push origin develop

# In .github/workflows/test.yml, set:
# on:
#   push:
#     branches: [ main, develop ]
#   pull_request:
#     branches: [ main, develop ]
```

---

## Step 7: Generate GitHub Token for CI/CD Deployments

If you want to auto-deploy after successful tests:

1. Go to GitHub **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token**
3. Select scopes:
   - `repo` (full control of private repos)
   - `workflow` (update GitHub Actions workflows)
4. Copy the token and save securely
5. Add to **Repository Secrets** as `GH_TOKEN`

---

## Step 8: Monitor & Manage

### Check CI/CD Status

```bash
# After pushing
git push origin main

# Watch GitHub Actions run (Actions tab)
# Green checkmark = all tests passed ✅
# Red X = fix required ❌
```

### View Logs

```bash
# Locally
git log --oneline -5
git log --graph --oneline --all

# On GitHub: Actions tab → click workflow run → see output
```

### Update Dependencies

```bash
# Locally update requirements.txt
pip install --upgrade google-genai fastapi

# Save updated versions
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "chore: upgrade dependencies"
git push origin main
```

---

## Step 9: Protect Main Branch (Optional)

On GitHub:

1. Go to **Settings** → **Branches**
2. Click **Add rule** under "Branch protection rules"
3. Pattern: `main`
4. Enable:
   - ✅ Require pull request reviews before merging (2 reviews if team)
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
5. Save

This prevents direct pushes to `main` — forces PR workflow.

---

## Troubleshooting

### Authentication Error

```
fatal: Authentication failed for 'https://github.com/YOUR_USERNAME/saas-agent-v2.git/'
```

**Solution:**
- HTTPS: Use GitHub Personal Access Token instead of password
- SSH: Ensure `ssh-keygen` and keys are added (`ssh -T git@github.com`)

### .gitignore not working

```bash
# If files are already tracked, remove them
git rm --cached .env
git rm --cached *.db
git commit -m "Remove sensitive files from tracking"
```

### GitHub Actions fails

Check workflow logs:

1. Go to **Actions** → click failed workflow
2. Click the failing job
3. Expand logs to see error
4. Common issues:
   - Python version mismatch → fix in `test.yml`
   - Missing dependency → add to `requirements.txt`

---

## Deployment to Production

### From Termux/Linux

```bash
# SSH into device
ssh user@device

# Clone repo
git clone https://github.com/YOUR_USERNAME/saas-agent-v2.git
cd saas-agent-v2

# Install & run
bash install.sh
source venv/bin/activate
export GEMINI_API_KEY="..."
python main.py
```

### Using GitHub Releases

```bash
# Create a tagged release
git tag -a v2.0.0 -m "Production release"
git push origin v2.0.0

# On GitHub: Releases → Create Release from tag
# Add installation notes, link to download
```

---

## Version Control Best Practices

| Do | Don't |
|---|---|
| ✅ Commit often (small, logical chunks) | ❌ Giant commits with 10+ files |
| ✅ Clear commit messages | ❌ "fix", "update", "asdf" |
| ✅ Branch for features | ❌ Push directly to main |
| ✅ Review PRs before merge | ❌ Auto-merge everything |
| ✅ Use .gitignore | ❌ Commit .env, API keys, *.db |
| ✅ Tag releases | ❌ No versioning |

---

## Quick Commands Reference

```bash
# View status
git status

# See changes
git diff                    # unstaged
git diff --cached           # staged
git log --oneline -10       # recent commits

# Undo changes
git checkout -- file.py     # discard file changes
git reset HEAD file.py      # unstage file
git revert COMMIT_HASH      # undo a commit

# Branch management
git branch                  # list branches
git branch -D branch-name   # delete branch
git checkout -b new-feature # create & switch

# Push/pull
git push origin branch-name # push
git pull origin main        # fetch & merge

# Stash (temp save)
git stash                   # save changes
git stash pop               # restore changes
```

---

## Support

- **GitHub Issues**: Create issues for bugs/features
- **GitHub Discussions**: Questions & ideas
- **Pull Requests**: Contribute changes

---

**You're all set!** 🚀 Your code is now in production-ready git with CI/CD. Push frequently, review PRs, and enjoy deterministic automation!
