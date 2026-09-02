---
name: swarm-architecture
description: Guide and architectural pattern for Agent Swarm Task Delegation and Nano-Segmentation.
---

# Agent Swarm Nano-Segmentation

This skill documents the methodology used to orchestrate a distributed agent swarm for writing codebases securely and efficiently without looping errors.

## The Tri-Agent Workflow

1. **Micro-Agents (The Writers)**
   - Context-free. They only receive an isolated "Identity Tag" (e.g., `[NANO-03:WASM_ENG]`) and a specific reasoning prompt.
   - They write code for only that specific chunk and send it to the Code-Master.

2. **Code-Master-Analyzer (The Validator)**
   - Receives snippets from Micro-Agents.
   - Auto-scales with task loads.
   - Runs syntax, safety, and integration tests on the code chunk.
   - Sends success/error feedback back to the Micro-Agent without entering infinite polling loops. 

3. **Codebase-Integrator (The Compiler)**
   - Only receives code chunks that have been marked "Success" by the Code-Master.
   - Responsible for wiring the dependencies, writing the imports, and generating the final monolithic codebase.
   - Often outputs a single `generate_codebase.py` script that can be executed entirely offline to write the clean codebase to disk instantly.

## Why this is superior:
- Prevents context window explosion.
- Stops "hallucination loops" where one agent constantly overwrites another agent's files.
- Separates writing (Micro), testing (Master), and structuring (Integrator).
