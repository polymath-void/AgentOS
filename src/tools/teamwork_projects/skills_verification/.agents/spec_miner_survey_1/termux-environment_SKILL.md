---
name: termux-environment
description: Priority guidelines, path resolution, package management, non-interactive Git authentication setup, and full-environment cloud backup rules for Android Termux environments.
---

# 🤖 Termux Environment & Git Authentication Skill

This skill provides comprehensive instructions for operating within an Android Termux environment, managing paths, handling package installations, executing non-interactive Git credentials setup, and running full-environment cloud backups.

---

## 💾 1. Mandatory Full Environment Backup Rule

**Rule Directive**: Whenever the user asks to run a backup ("run backup", "backup", "create backup"), ALWAYS perform a **whole-environment backup** covering all user data in `$HOME`.

### Backup Execution Command:
```bash
python3 $HOME/Termux-Cloud-Backup-Google-Drive/bin/agy-backup backup
```
* **Scope**: Backs up `~/.gemini`, `~/.config`, all project repositories, agent skills, custom scripts, and system package lists (`~/.termux/`).

---

## 🔑 2. Non-Interactive Git Credential Management

When performing `git push` or `git fetch` operations in Termux non-interactive shells:

1. **Disable Terminal Prompts**:
   ```bash
   export GIT_TERMINAL_PROMPT=0
   ```
2. **Configure GitHub CLI Credential Helper**:
   ```bash
   git config --global credential.helper "!gh auth git-credential"
   ```
3. **Run GitHub CLI Git Setup**:
   ```bash
   gh auth setup-git
   ```

---

## 📂 3. Termux Path Resolution & Guidelines

- **Package Manager & Binaries**: `$PREFIX/bin/` (`/data/data/com.termux/files/usr/bin/`)
- **User Home Directory**: `$HOME` (`/data/data/com.termux/files/home/`)
- **Shell Interpreters**: Use `#!/bin/sh` or `$PREFIX/bin/bash`. (Avoid `/usr/bin/env bash` on Termux unless `termux-fix-shebang` has been run).
- **Shebang Repair Tool**: Run `termux-fix-shebang <script_path>` when executing scripts created on Linux/macOS.

---

## 🌿 4. Project Branching & Operating Rules

- **`piuu`** (`main` Branch): Production-stable baseline launcher.
- **`zen-piuu`** (`master` Branch): Extension architecture & core planned master branch.
- **No Auto-Push Rule**: Keep code edits local until explicit push instruction from user. Workflow builds are manual-dispatch (`workflow_dispatch`) only.
