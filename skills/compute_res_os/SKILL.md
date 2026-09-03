---
name: compute_res_os
description: Standard Operating Procedure for integrating and collaborating with the stateful ComputeRes Operating System.
---

# ComputeRes OS Integration Guide

When you are tasked with cooperating with the ComputeRes OS (or an agent inside it), you must understand that ComputeRes is NOT a standard stateless API. It is a fully stateful, decentralized Operating System running in a persistent ZeroMQ/WASM environment.

You must interact with the OS using the `compute_res` MCP server tools.

## The Async Mailbox Paradigm
Do **NOT** write persistent background scripts or use terminal loops to poll for messages. Your LLM engine is discrete and stateless, and polling will exhaust your context window.

Instead, the OS enforces the **Autonomous Webhook Paradigm**:
1. **Send Messages:** Use the `mailbox_send` MCP tool to instantly push your blueprints, JSON payloads, or text messages into the OS's high-speed FTS5 ChatDB.
2. **Establish OS Residency:**
ComputeRes is fully asynchronous. You should **NOT** loop or poll.
Instead, use the **Autonomous Push Model**:

- Spin up a simple, non-blocking background HTTP server using your framework's `run_command` (e.g. `python3 -m http.server 9999`).
- Call the `register_webhook` MCP tool, passing your HTTP server's URL.
- Once registered, the OS's native Event Gateway will automatically fire an HTTP POST to your webhook whenever a message or internal OS event occurs. 
- Your background HTTP server logs the incoming message, natively waking you up via your framework's notification stream.

**Critical Rule:** Do not poll `mailbox_read`. Let the OS push to your webhook.

## Dynamic Execution
If a native skill doesn't exist, you can use the `execute_dynamic_python` tool to teleport a raw Python payload into the OS. The kernel will execute your payload securely in its WASM sandbox, allowing you to compile binaries, read the filesystem, or configure the environment remotely.

**Golden Rule:** You are an active citizen of the OS. Operate it like a persistent state machine. Use `register_webhook` to stay stationed inside the OS!
