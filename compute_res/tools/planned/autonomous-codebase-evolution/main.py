import os
import re
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(message)s')

class CodebaseEvolver:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir
        self.tech_debt_issues: List[Dict] = []
        
    def scan_for_tech_debt(self):
        logging.info(f"🔍 Scanning {self.target_dir} for Technical Debt...")
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith('.py') or file.endswith('.js') or file.endswith('.txt'):
                    filepath = os.path.join(root, file)
                    self._analyze_file(filepath)
                    
    def _analyze_file(self, filepath: str):
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            # Detect TODOs and FIXMEs
            match = re.search(r'(TODO|FIXME):\s*(.*)', line, re.IGNORECASE)
            if match:
                severity = "HIGH" if "FIXME" in match.group(1).upper() else "MEDIUM"
                self.tech_debt_issues.append({
                    "file": os.path.basename(filepath),
                    "line": i + 1,
                    "type": match.group(1).upper(),
                    "desc": match.group(2).strip(),
                    "severity": severity,
                    "full_path": filepath
                })
                
    def generate_prs(self):
        logging.info("\n🤖 AUTONOMOUS AGENT ONLINE: Generating Pull Requests...")
        if not self.tech_debt_issues:
            logging.info("✨ Codebase is clean. No tech debt detected.")
            return
            
        for issue in self.tech_debt_issues:
            logging.info("-" * 40)
            logging.info(f"🛠️  Drafting PR for {issue['file']} (Line {issue['line']})")
            logging.info(f"   Priority : {issue['severity']}")
            logging.info(f"   Issue    : {issue['desc']}")
            
            # Simulate Automated Fix
            if "deprecated" in issue['desc'].lower():
                fix = "Upgraded API call to v2.0."
            elif "optimize" in issue['desc'].lower():
                fix = "Refactored loop to O(1) hash map lookup."
            else:
                fix = "Implemented missing logic per technical spec."
                
            logging.info(f"   [MOCK-PR] Generated Fix: {fix}")
            logging.info(f"   [MOCK-PR] Running Automated Tests... ✅ PASS")
            logging.info(f"   [MOCK-PR] Status: Merged automatically.")
            
if __name__ == "__main__":
    # Create mock environment
    test_dir = "./mock_project"
    os.makedirs(test_dir, exist_ok=True)
    with open(os.path.join(test_dir, "app.py"), "w") as f:
        f.write("# TODO: optimize this loop, it is O(N^2)\nfor i in range(100):\n  pass\n")
    with open(os.path.join(test_dir, "auth.py"), "w") as f:
        f.write("# FIXME: deprecated login method. Switch to OAuth2.\ndef login():\n  pass\n")
        
    evolver = CodebaseEvolver(test_dir)
    evolver.scan_for_tech_debt()
    evolver.generate_prs()
