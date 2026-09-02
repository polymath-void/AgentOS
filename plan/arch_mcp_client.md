# AgentOS MCP Standalone Client: Architectural Blueprint

## 1. Overview
The MCP Standalone Client acts as the critical bridge connecting any external AI Agent (the "Brain") to the AgentOS ecosystem. Its primary responsibility is to manage the Model Context Protocol (MCP) lifecycle: connection establishment, tool discovery (JSON Schema parsing), and execution routing via the AgentOS Gateway (`mcp_server.py`). 

By strictly isolating protocol mechanics, the client ensures the LLM's prompt logic, reasoning, and memory remain entirely decoupled from the underlying execution infrastructure and ZeroMQ broker.

## 2. Core Architecture

The Standalone Client consists of three main modules:
- **Transport Layer (Connection Manager):** Handles the I/O stream (e.g., Stdio subprocess piping, or WebSockets/SSE) to communicate natively with the AgentOS Gateway.
- **Discovery Engine:** Requests, parses, and normalizes the JSON Schemas for available tools provided by AgentOS.
- **Execution Engine:** Formats JSON-RPC 2.0 requests for tool invocation, dispatches them to the Gateway, and processes synchronous or asynchronous responses.

## 3. Protocol Mechanics & Message Flow

### 3.1. Connection & Initialization
1. **Client Spawn/Connect:** The client initializes a connection to the AgentOS `MCPGateway`. Depending on the deployment, this involves spawning `mcp_server.py` as a subprocess communicating over `stdin`/`stdout`, or connecting to an exposed network socket.
2. **Handshake:** The client sends an `initialize` JSON-RPC request to negotiate protocol version and capabilities.
3. **Acknowledgment:** The Gateway responds with its supported features, officially acknowledging the `tools` capability.

### 3.2. Tool Discovery (`tools/list`)
1. **Request:** The client dispatches a `tools/list` JSON-RPC request.
2. **Response Processing:** The Gateway returns a list of tools, each containing a name, description, and an input schema defined in standard JSON Schema format.
3. **Schema Normalization:** The client parses the JSON Schema. It standardizes the schema representation so the external LLM agent receives a clean, uniform list of callable functions, completely masking the complexity of the underlying JSON-RPC payload.

### 3.3. Command Execution (`tools/call`)
1. **Payload Construction:** When the external agent decides to invoke a tool, the client constructs a standardized JSON-RPC 2.0 request:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "<unique_id>",
     "method": "tools/call",
     "params": {
       "name": "<tool_name>",
       "arguments": { ... }
     }
   }
   ```
2. **Dispatch to Gateway:** The client sends this string payload to the transport layer, which feeds it into `MCPGateway.handle_mcp_request(rpc_request: str)`.
3. **Gateway Routing:** The Gateway translates this into a ZeroMQ IPC message targeting the `prime_agent`.
4. **Response Handling:**
   - **On Success:** The client parses the JSON-RPC result (extracting the `content` array) and returns the standard text payload back to the LLM.
   - **On Error/Timeout:** The client captures JSON-RPC error codes (e.g., `-32603`) or Gateway timeout messages, translating them into programmatic exceptions that the external agent can gracefully handle or retry.

## 4. Decoupled Interface Design

The client exposes a highly abstracted API intended for the LLM's executor loop. The "Brain" only interacts with this clean interface.

```python
class AgentOSMCPClient:
    async def connect(self) -> None:
        """
        Establishes transport connection to the AgentOS Gateway.
        Handles the JSON-RPC 'initialize' handshake.
        """
        pass

    async def get_tools(self) -> list[dict]:
        """
        Sends 'tools/list' request.
        Returns a sanitized list of tools and their JSON schemas for the LLM to ingest.
        """
        pass

    async def call_tool(self, name: str, arguments: dict) -> str:
        """
        Sends 'tools/call' request.
        Abstracts the JSON-RPC framing and returns the raw string result directly to the LLM.
        """
        pass
```

## 5. Resiliency & Error Handling
- **Gateway Timeouts:** If the Gateway's ZeroMQ socket times out (default 5000ms), the client intercepts the timeout payload from the Gateway. It must expose this clearly to the LLM without crashing the client loop.
- **Client-Side Schema Validation (Optional):** Before transmitting the `tools/call` payload, the client may optionally validate the arguments against the cached JSON schema to prevent malformed requests from reaching the Gateway, saving IPC bandwidth and time.
