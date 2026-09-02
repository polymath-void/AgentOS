import os
import time
import hashlib
import shutil
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SelfHealingWatchdog:
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        self.backup_dir = os.path.join(watch_dir, ".backups")
        self.state: Dict[str, str] = {}
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)

    def _hash_file(self, filepath: str) -> str:
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except FileNotFoundError:
            return ""

    def snapshot(self):
        """Creates initial backups and stores hashes for all files in the watch directory."""
        logging.info(f"Taking snapshot of {self.watch_dir}...")
        for filename in os.listdir(self.watch_dir):
            filepath = os.path.join(self.watch_dir, filename)
            if os.path.isfile(filepath) and not filename.startswith('.'):
                file_hash = self._hash_file(filepath)
                self.state[filepath] = file_hash
                shutil.copy2(filepath, os.path.join(self.backup_dir, filename))
                logging.info(f"Snapshotted {filename} (Hash: {file_hash[:8]}...)")

    def monitor(self, interval: int = 2):
        """Continuously watches for unauthorized changes and rolls them back."""
        logging.info("Watchdog active. Monitoring for unauthorized changes...")
        try:
            while True:
                for filepath, original_hash in self.state.items():
                    if not os.path.exists(filepath):
                        continue # Skip deleted files for this simple implementation
                    
                    current_hash = self._hash_file(filepath)
                    if current_hash != original_hash:
                        filename = os.path.basename(filepath)
                        logging.warning(f"UNAUTHORIZED CHANGE DETECTED: {filename}")
                        logging.warning(f"Initiating Self-Healing Protocol...")
                        
                        backup_path = os.path.join(self.backup_dir, filename)
                        if os.path.exists(backup_path):
                            shutil.copy2(backup_path, filepath)
                            logging.info(f"✅ {filename} restored to original state.")
                        else:
                            logging.error(f"Failed to restore {filename}. Backup missing!")
                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Watchdog terminated by user.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Self-Healing Filesystem Watchdog")
    parser.add_argument("--dir", type=str, default=".", help="Directory to protect")
    args = parser.parse_args()
    
    target = os.path.abspath(args.dir)
    watchdog = SelfHealingWatchdog(target)
    watchdog.snapshot()
    watchdog.monitor()
