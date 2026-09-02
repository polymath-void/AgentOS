# AgentOS: Core Execution Layer Architecture Blueprint

## 1. Abstract
AgentOS is the underlying environment for external AI agents, exposed entirely via the Model Context Protocol (MCP). It is a headless, brainless substrate where agents act as the intelligence piloting the system. This blueprint details the Core Execution Layer, specifically focusing on the translation of MCP logical intents to ZeroMQ (0MQ) IPC messages and the real-time dynamic exposure of hot-loaded skills via the MCP Gateway.

## 2. Core Execution Layer: Component Architecture
- **External AI Agent**: The "brain" connecting via MCP.
- **MCP Gateway (Front-end)**: The entry point. Translates MCP JSON-RPC requests into standardized ZeroMQ messages.
- **ZeroMQ IPC Broker (The Nervous System)**: A `ROUTER/DEALER` broker that routes messages asynchronously between the Gateway, the Kernel, and the SkillRegistry.
- **Python Kernel (The Executor)**: Evaluates code, executes system-level operations, and maintains session state.
- **Dynamic SkillRegistry**: Manages hot-loading of Python scripts, parsing them for metadata, executing them, and broadcasting capability updates to the MCP Gateway.

## 3. Intent Mapping: MCP to ZeroMQ

When an external agent decides to act, it formulates an intent as an MCP `execute_tool` request. This must be efficiently mapped to the IPC layer.

### 3.1. The Translation Pipeline
1. **MCP Request Reception**: The MCP Gateway receives the standard JSON-RPC request over stdio, HTTP/SSE, or WebSockets.
2. **Intent Encapsulation (Message Envelope)**: The Gateway constructs a ZeroMQ multipart message. The use of multipart frames prevents serialization overhead for routing data.
   - **Frame 1**: Routing Identity (e.g., `skill_worker_1` or `kernel_session_A`)
   - **Frame 2**: Message Type (e.g., `REQ_EXEC_SKILL`, `REQ_EVAL_CODE`, `REQ_SYS_INFO`)
   - **Frame 3**: Payload (MessagePack or JSON serialized arguments, execution UUID, and context metadata)
3. **Dispatch**: The Gateway, acting as a `DEALER` socket, pushes the message to the ZeroMQ IPC Broker (a `ROUTER` socket).
4. **Execution & Acknowledgment**: The Broker forwards the message to the appropriate worker. The worker instantly replies with an `ACK` (to prevent timeout) and processes the payload.
5. **Resolution**: Upon completion, the worker replies back through the Broker to the Gateway, which unpacks the Payload and maps it back to an MCP JSON-RPC Response.

### 3.2. Asynchronous Streaming and Long-Running Intents
Agents often initiate tasks that take time (e.g., training a model, scanning a large directory). AgentOS maps these to asynchronous ZeroMQ Pub/Sub patterns.
- **Execution UUIDs**: Every request gets a unique task ID.
- **Progress Streams**: The Gateway subscribes to a ZeroMQ `PUB` socket (`Topic: stream.<UUID>`). As the worker emits stdout/stderr or custom progress events, the Gateway forwards these to the agent via MCP custom notifications or resource updates.

## 4. Real-time Capability Exposure via SkillRegistry

A defining feature of AgentOS is its ability to mutate its capability surface area in real-time. The registry hot-loads python scripts and immediately exposes them as new MCP tools.

### 4.1. The Hot-loading Lifecycle
1. **FS Event / Ingestion**: The SkillRegistry monitors a `/skills` directory via `inotify` or provides a ZeroMQ endpoint for skill ingestion.
2. **AST Parsing & Introspection**: Upon detecting a new script (`.py`), the Registry parses the Abstract Syntax Tree (AST). It extracts:
   - Function signatures and Type Hints (mapped to JSON Schema parameters).
   - Docstrings (mapped to the MCP Tool description).
3. **Sandboxed Instantiation**: The skill is loaded into a dynamically created, isolated Python namespace (using `importlib` and customized module loaders).
4. **Capability Broadcast**: The SkillRegistry publishes a ZeroMQ message on a `PUB` socket (Topic: `SYS_CAPABILITY_UPDATE`). The payload contains the newly generated JSON Schema for the tool.

### 4.2. Dynamic MCP Tool Updates (The Feedback Loop)
1. **Gateway Subscription**: The MCP Gateway is permanently subscribed to the `SYS_CAPABILITY_UPDATE` topic.
2. **State Reconciliation**: Upon receiving an update, the Gateway merges the new tool schema into its internal routing table.
3. **MCP Notification**: The Gateway immediately issues a `notifications/tools/list_changed` JSON-RPC notification to all connected MCP clients (Agents).
4. **Agent Re-fetch**: The Agent, adhering to the MCP spec, responds by requesting the new list of tools (`tools/list`), seamlessly integrating the new capability into its action space without restarting the connection.

## 5. Fault Tolerance and Edge Cases
- **Worker Death**: If a Python kernel crashes during execution, the ZeroMQ Broker detects the broken pipe. It returns an `EXEC_FAILED` message to the Gateway, which maps to an MCP Error response, allowing the Agent to attempt a recovery strategy.
- **Schema Validation**: Before broadcasting a capability update, the SkillRegistry enforces strict JSON Schema validation. Invalid skills are rejected, and an error is logged to the system topic.
