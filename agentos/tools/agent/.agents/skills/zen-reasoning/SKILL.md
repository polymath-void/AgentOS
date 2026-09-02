---
name: zen-reasoning
description: Guidelines for implementing the Zen Reasoning Protocol for hierarchical agent delegation.
---

# Zen Reasoning Protocol

The Zen Reasoning Protocol is a specialized hierarchical problem-solving architecture for our agents.

## 1. The Delegation Chain
- **Polymath (Main Agent):** The orchestrator. Receives the raw user input, breaks down the problem, and delegates it. It acts as the final synthesizer that delivers the "pure solution".
- **Master Agent (●>):** Manages large segments of a task. Distributes specific tasks to Sub Agents.
- **Sub Agent (●●):** Handles domain-specific logic. Delegates granular, micro-level problems to Micro Agents.
- **Micro Agent (<●●>):** Executes specific, atomic operations (like parsing a string, executing a search, or formatting a result) and returns the data up the chain.

## 2. Three-Step Loop
When an agent processes a task, it must follow this loop:
1. **Step-back Reflection:** Analyze the context. What is the actual goal? What dependencies are needed?
2. **Chain-of-Thought:** Break down the execution into logical steps.
3. **Self-Critique:** Review the steps. Are they optimal? Is there a faster or more memory-efficient way to execute this?

## 3. Implementation in Rust
When implementing agents in the `src/subagents/mod.rs` codebase:
- Use asynchronous recursive structures (`Pin<Box<dyn Future>>`) to handle the delegation depth.
- Ensure strict timeout and depth limit configurations (e.g., via `/config max_depth`) to prevent infinite recursion.
- Log the reasoning steps securely using the `LongTermMemory` module.
