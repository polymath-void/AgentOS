# Autonomous Codebase Evolution

## Overview
A technical debt analyzer that autonomously detects vulnerabilities and drafts mock pull requests.

## Features
- **Recursive Scanning**: Parses all target codebase directories for `.py`, `.js`, and `.txt` files.
- **Debt Detection**: Identifies and flags `TODO` and `FIXME` comments.
- **Severity Classification**: Automatically categorizes issues into MEDIUM or HIGH priority.
- **Mock PR Generation**: Drafts automated fixes, simulates testing pipelines, and merges.

## Usage
```bash
python3 main.py
```
