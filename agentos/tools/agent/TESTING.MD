# Operational & Testing Guide

## Running the Agent
1. **Set your API Key:**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
2. **Execute:**
   ```bash
   cargo run
   ```

## Testing Strategy
The agent relies on network-bound integration with Gemini and OS-bound shell execution.

### Integration Testing (Local)
Create `tests/integration_tests.rs` to simulate the orchestrator's interactions:
- **Test 1:** Verify tool registration in `~/.polymath_agent/tools/`.
- **Test 2:** Verify tool execution via `execute_shell_command`.
- **Test 3:** Verify memory buffer pruning in `ShortTermMemory`.

### Simulation Script
Use this bash script (`tests/smoke_test.sh`) for a quick verification:
```bash
#!/bin/bash
# Simple smoke test
echo "Running system check..."
./target/debug/polymath-void-agent <<EOF
echo "Hello World"
exit
EOF
```
