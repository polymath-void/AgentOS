# ComputeRes Integration Blueprint

## 1. Overview
ComputeRes elevates the local agent swarm playground into a cohesive operating system layer for AI agents. This blueprint details the integration architecture for:
- Model Context Protocol (MCP) servers
- Unified Logging system
- Inter-Process Communication (IPC)
- Tool Registries

## 2. Architecture Layout

### 2.1 Model Context Protocol (MCP) Integration
External MCP servers provide the connective tissue to specialized, out-of-process resources.
- **MCP Daemon (`mcpd`)**: A background service that manages connections to configured MCP servers.
- **Resource Proxying**: Transparently map MCP resources into a virtual filesystem (VFS) within ComputeRes.
- **Tool Mapping**: Tools exposed via MCP are dynamically registered in the central Tool Registry.

### 2.2 Unified Logging (`syslog` for Agents)
All components, including standalone agents, background tasks, and MCP servers, stream logs to a unified sink.
- **Log Format**: Structured JSON Lines (JSONL) with required fields: `timestamp`, `agent_id`, `component`, `level`, `message`, `context`.
- **Log Aggregator**: A lightweight service (like fluent-bit or custom Python script) runs locally to parse, index, and store these logs.
- **Agent Accessible Logs**: The unified log stream is exposed as an MCP resource or specialized read-tool so agents can debug each other's failures.

### 2.3 Inter-Process Communication (IPC)
Fast, reliable messaging is the core of swarm coordination.
- **Message Broker**: ZeroMQ or Redis pub-sub depending on scale (ZeroMQ preferred for zero-dependency local setups).
- **Communication Patterns**:
    - *Request-Reply*: For direct agent-to-agent delegation (e.g., Subagent calls).
    - *Publish-Subscribe*: For system-wide events (e.g., File modifications, Timer triggers, Error cascades).
- **Protocols**: Use Protocol Buffers or standardized JSON schemas for IPC payloads to ensure strict typing across language boundaries (e.g., Python agent communicating with Node.js agent).

### 2.4 Tool Registry
A dynamic, centralized registry of all capabilities available to the swarm.
- **Registration**: Agents, scripts, and MCP servers announce their capabilities to the registry upon startup.
- **Discovery**: Agents query the registry by semantic intent ("find me a tool to edit PDF") or exact name.
- **Access Control**: The registry enforces permissions (e.g., sandboxed agents cannot access the `run_command` tool).

## 3. Integration Flow Example
1. **Startup**: ComputeRes starts. The Message Broker and Unified Logging services initialize.
2. **MCP Connection**: `mcpd` reads config, connects to a Supabase MCP server, and registers `list_tables` and `execute_sql` in the Tool Registry.
3. **Agent Invocation**: The Orchestrator agent receives a task. It queries the Tool Registry for database tools.
4. **Tool Execution**: Orchestrator sends an IPC message to `mcpd` requesting `execute_sql`.
5. **Logging**: `mcpd` logs the query to Unified Logging. It proxies the request to the MCP server.
6. **Response**: The result flows back via IPC to the Orchestrator, which logs its completion.
