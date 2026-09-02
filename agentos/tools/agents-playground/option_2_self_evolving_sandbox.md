# Option 2: Self-Evolving Agent Mutation Sandbox (EvolvOS)

## 🌀 Self-Evolution & Mutation Loop

When the agent detects a missing skill required to solve a task:
1. **Plan & Synthesize**: It writes a Python script containing the missing functionality (including inputs, core logic, and basic test assertions).
2. **Sandbox Run**: The playground runs the script in an isolated subprocess with restricted permissions and capture of all outputs.
3. **Traceback Correction**: If the script crashes or raises an assertion error, the agent parses the traceback error and rewrites the script code recursively.
4. **Dynamic Import**: Once the script executes successfully and passes all test assertions, it is loaded dynamically into the agent's active memory as a registered skill.

## 📂 Proposed Folder Structure

```text
agents-playground/
├── requirements.txt        # google-genai, rich, prompt_toolkit
├── evolvos.py              # Main Evolution entry point
├── core/
│   ├── __init__.py
│   ├── agent.py            # Base agent that flags missing capabilities
│   ├── evolution.py        # The Synthesize-Sandbox-Debug loop manager
│   └── sandbox.py          # Subprocess executor for safe code execution
└── library/                # Folder where evolved scripts are saved
    ├── __init__.py
    ├── registry.json       # Metadata and schemas for evolved skills
    └── evolved_skills/     # Dynamic script storage directory
```

## ⚙️ Core Technical Implementation Details

### 1. Isolated Subprocess Sandbox (`core/sandbox.py`)
Runs code in a clean environment to ensure safety:
```python
import subprocess
import sys
from pathlib import Path

def run_test_sandbox(script_path: Path, timeout: int = 5):
    try:
        res = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "success": res.returncode == 0,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "exit_code": res.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Execution timeout exceeded", "exit_code": -1}
```

### 2. Dynamic Skill Loader (`core/evolution.py`)
Loads new skills in real time without restarting the terminal session:
```python
import importlib.util
from pathlib import Path

def load_skill_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```
Upon load, the function is extracted and registered into the agent's available tools array.
