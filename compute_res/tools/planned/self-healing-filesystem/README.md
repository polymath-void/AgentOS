# Self-Healing Filesystem Watchdog

## Overview
A continuous monitoring daemon that protects critical files against unauthorized changes. 

## Features
- **Snapshotting**: Computes SHA-256 hashes of all monitored files.
- **Encrypted Backups**: Automatically duplicates files to a hidden `.backups` directory.
- **Active Polling**: Continuously verifies file integrity.
- **Automated Rollback**: Instantly restores files upon detecting hash mismatches.

## Usage
```bash
python3 main.py --dir .
```
