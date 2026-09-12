# SkillsHub Integration Blueprint

## 1. MCP Tool Integration Design

To enable external agents to interact with the SkillsHub dynamically, we will expose the following MCP tools through the `mcp_server.py`:

*   **`publish_skill`**:
    *   **Description**: Registers a new custom skill with the SkillsHub DB.
    *   **Parameters**:
        *   `skill_name` (string): Unique identifier for the skill.
        *   `description` (string): Human-readable description of what the skill does.
        *   `payload` (string/json): The execution logic, instructions, or API schema defining the skill.
        *   `tags` (list[string]): Optional categories for easier discovery.
    *   **Response**: Success confirmation or validation error.
*   **`query_skills`**:
    *   **Description**: Searches the SkillsHub DB for available skills.
    *   **Parameters**:
        *   `query` (string): Text search across skill names and descriptions.
        *   `tags` (list[string]): Filter by tags.
    *   **Response**: A list of matched skills with metadata and access instructions.
*   **`invoke_skill`** (Optional but recommended):
    *   **Description**: Triggers a published skill through the OS.
    *   **Parameters**:
        *   `skill_name` (string)
        *   `arguments` (json)

These tools will act as standard MCP definitions, allowing compliant agents to discover and utilize the Skills Routing Protocol natively.

## 2. Implementation Blueprint

### Modifying `mcp_server.py`

1.  **Tool Registration**: We will define the `publish_skill` and `query_skills` schemas in the MCP server's tool registry.
2.  **Request Handling**: When an MCP request for these tools is received, `mcp_server.py` will validate the schema and construct an internal event payload.
3.  **Kernel Communication**: Instead of directly interacting with a database, `mcp_server.py` will route these requests to the core OS kernel via the established IPC or event bus mechanism. We will introduce a new event type specifically for SkillsHub operations to differentiate them from standard webhook events.

### Modifying Core OS Kernel

1.  **Event Router Update**: Update the kernel's central event router to recognize the new SkillsHub event types (e.g., `EVENT_TYPE_SKILL_PUBLISH`, `EVENT_TYPE_SKILL_QUERY`).
2.  **SkillsHub Service**: Introduce an isolated `SkillsHubService` module within the kernel.
    *   This service acts as the controller for the SkillsHub DB.
    *   It listens for SkillsHub events dispatched by the event router.
    *   It executes the necessary CRUD operations on the database (SQLite, in-memory struct, etc.).
3.  **Preserving Webhook Architecture**:
    *   By using distinct event types and routing logic, standard webhook payloads (e.g., `EVENT_TYPE_WEBHOOK_RECEIVE`) remain completely untouched.
    *   The Webhook dispatcher and SkillsHub dispatcher will operate in parallel, ensuring no interference.
    *   If a published skill needs to trigger a webhook as part of its payload, the `SkillsHubService` can construct and emit standard webhook events back into the router, fully leveraging the existing architecture without tightly coupling the systems.

### Data Flow Example (Publish)
1.  Agent calls `publish_skill` via MCP.
2.  `mcp_server.py` constructs `SkillsHubEvent(type="publish", data={...})`.
3.  Kernel router receives event, sees `type="publish"`, routes to `SkillsHubService`.
4.  `SkillsHubService` validates and writes to DB, returns `Success`.
5.  Kernel router passes `Success` back to `mcp_server.py`.
6.  `mcp_server.py` responds to Agent via MCP.
