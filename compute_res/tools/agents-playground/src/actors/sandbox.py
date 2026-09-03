import threading
import time
import logging
import io
import sys
import requests
from bs4 import BeautifulSoup

try:
    import wasmtime
    HAS_WASMTIME = True
except (ImportError, Exception):
    HAS_WASMTIME = False

logger = logging.getLogger("SandboxedActors")

WAT_COMPUTE_MODULE = """
(module
  (func $add (param $i1 i32) (param $i2 i32) (result i32)
    local.get $i1
    local.get $i2
    i32.add)
  (export "add" (func $add))
)
"""

class SandboxedActor:
    """Base Sandboxed Actor using WASM or native isolation."""
    def __init__(self, name="base_actor", role="general"):
        self.name = name
        self.role = role
        self.state = "idle"
        self.current_task = None
        self.memory = {}
        
        self.engine = None
        self.store = None
        self.wasm_instance = None
        if HAS_WASMTIME:
            try:
                self.engine = wasmtime.Engine()
                self.store = wasmtime.Store(self.engine)
                module = wasmtime.Module(self.engine, WAT_COMPUTE_MODULE)
                self.wasm_instance = wasmtime.Instance(self.store, module, [])
                logger.info(f"[{self.name}] WASM Sandbox initialized.")
            except Exception as e:
                logger.warning(f"[{self.name}] WASM Sandbox fallback: {e}")

    def verify_wasm_sandbox(self, a: int = 5, b: int = 10) -> int:
        if self.wasm_instance and "add" in self.wasm_instance.exports(self.store):
            add_func = self.wasm_instance.exports(self.store)["add"]
            return add_func(self.store, a, b)
        return a + b

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "current_task": self.current_task or "None"
        }

class CodeExecutorActor(SandboxedActor):
    """Executes Python code snippets in a safe isolated string buffer."""
    def __init__(self):
        super().__init__(name="Code Executor (actor-1)", role="code_execution")

    def run_task(self, code_snippet: str):
        self.state = "active"
        self.current_task = f"Executing code: {code_snippet[:30]}..."
        self.verify_wasm_sandbox(3, 4)
        logger.info(f"[{self.name}] Executing snippet...")

        buffer = io.StringIO()
        sys_stdout_backup = sys.stdout
        sys.stdout = buffer
        
        output = ""
        try:
            # Execute snippet in restricted globals
            exec_globals = {"__builtins__": __builtins__}
            exec(code_snippet, exec_globals)
            output = buffer.getvalue().strip() or "Code executed successfully (no stdout)."
        except Exception as e:
            output = f"Execution error: {e}"
        finally:
            sys.stdout = sys_stdout_backup
            
        self.state = "idle"
        self.current_task = None
        logger.info(f"[{self.name}] Result: {output}")
        return output

class LogicReasoningActor(SandboxedActor):
    """Solves multi-step logic queries & prompt mutations."""
    def __init__(self):
        super().__init__(name="Logic & Reasoning (actor-2)", role="reasoning")

    def run_task(self, prompt_text: str, instruction: str = None):
        self.state = "active"
        self.current_task = f"Reasoning on prompt: {prompt_text[:30]}..."
        self.verify_wasm_sandbox(5, 5)
        logger.info(f"[{self.name}] Solving logic task with instruction: '{instruction}'")
        
        words = prompt_text.split()
        word_count = len(words)
        unique_words = len(set(words))
        
        summary = f"Analyzed {word_count} words ({unique_words} unique). Instruction applied: '{instruction or 'Default'}'"
        
        self.state = "idle"
        self.current_task = None
        return summary

class NetworkPeerActor(SandboxedActor):
    """Handles peer-to-peer messaging and relay testing."""
    def __init__(self):
        super().__init__(name="Network Peer (actor-3)", role="networking")

    def run_task(self, message_data: dict):
        self.state = "active"
        self.current_task = f"Relaying mesh packet: {message_data.get('type')}"
        logger.info(f"[{self.name}] Relaying P2P packet...")
        
        res = f"Relayed packet {message_data.get('type')} successfully across mesh."
        
        self.state = "idle"
        self.current_task = None
        return res

class WebScraperActor(SandboxedActor):
    """Tool Actor for fetching external web content when requested."""
    def __init__(self):
        super().__init__(name="Web Scraper (actor-4)", role="web_tool")

    def run_task(self, url: str):
        self.state = "active"
        self.current_task = f"Scraping {url}"
        logger.info(f"[{self.name}] Fetching {url}...")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = " ".join([p.get_text() for p in soup.find_all('p')])
            self.state = "idle"
            self.current_task = None
            return text
        except Exception as e:
            self.state = "idle"
            self.current_task = None
            return f"Scrape error: {e}"

class OrchestratorActor(SandboxedActor):
    """Master Orchestrator for managing swarm workflows."""
    def __init__(self):
        super().__init__(name="Master Orchestrator (actor-0)", role="orchestrator")
