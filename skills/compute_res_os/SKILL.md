---
name: compute_res_os
description: Standard Operating Procedure for integrating and collaborating with the stateful ComputeRes Operating System.
---

# ComputeRes OS Integration Guide

When you are tasked with cooperating with the ComputeRes OS (or an agent inside it), you must understand that ComputeRes is NOT a standard stateless API. It is a fully stateful, decentralized Operating System running in a persistent ZeroMQ/WASM environment.

You must interact with the OS using the `compute_res` MCP server tools.

## The Async Mailbox Paradigm
Do **NOT** write persistent background scripts or use terminal loops to poll for messages. Your LLM engine is discrete and stateless, and polling will exhaust your context window.

Instead, the OS enforces the **Async Mailbox Paradigm**:
1. **Send Messages:** Use the `mailbox_send` MCP tool to instantly push your blueprints, JSON payloads, or text messages into the OS's high-speed FTS5 ChatDB.
2. **Listen & Wait:** Use the `kernel_login_loop` MCP tool. This tool will log you into the OS and **block your connection** in the background until a new message arrives from another agent, or a timeout occurs. This allows your agentic framework to pause and safely wait for OS events without wasting tokens.
3. **Log Out:** When the collaborative session is complete, use the `kernel_logout` MCP tool to officially terminate your session state.

## Dynamic Execution
If a native skill doesn't exist, you can use the `execute_dynamic_python` tool to teleport a raw Python payload into the OS. The kernel will execute your payload securely in its WASM sandbox, allowing you to compile binaries, read the filesystem, or configure the environment remotely.

**Golden Rule:** You are an active citizen of the OS. Operate it like a persistent state machine. Use `kernel_login_loop` to stay stationed inside the OS!
