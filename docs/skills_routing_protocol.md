# Skills Routing Protocol (SRP) Architecture

## 1. Overview
The Skills Routing Protocol (SRP) is a core subsystem of the ComputeRes OS designed to facilitate the dynamic sharing, discovery, and adaptation of agentic skills across the swarm. By leveraging ZeroMQ for high-throughput Inter-Process Communication (IPC) and WebSockets for distributed external routing, SRP enables a decentralized, emergent capability marketplace where agents can publish their self-adapted skills and dynamically request task-specific capabilities.

## 2. Core Components

### 2.1. Skill Registry (The Nexus)
- **State:** Maintains an in-memory graph of all active, published skills within a node, tracking lineage and success metrics.
- **IPC Interface:** Binds a ZeroMQ `ROUTER` socket for handling incoming requests and a `PUB` socket for broadcasting registry updates to the swarm.

### 2.2. Agent Interfaces (The Nodes)
- **Publisher Mode:** Agents use a ZeroMQ `DEALER` or `REQ` socket to register newly synthesized or adapted skills.
- **Consumer Mode:** Agents use a ZeroMQ `REQ` socket to query the registry for specific niches.
- **Adapter Mode:** Agents download, mutate, and re-publish skills based on task-specific feedback loops.

### 2.3. External Swarm Gateway
- **Transport:** WebSockets.
- **Function:** Bridges local ZeroMQ skill registries with external ComputeRes nodes, allowing for global swarm skill discovery. It acts as a transparent proxy for `SKILL_QUERY` and `SKILL_REGISTER` events across network boundaries.

## 3. Data Structures & Serialization

Skills are serialized as YAML documents with structured metadata to allow for rapid parsing, filtering, and execution by the native agent loop.

### 3.1. Skill Schema (YAML)
```yaml
id: "skill_fs_traversal_v2"
author: "agent_8f2a"
niche: ["filesystem", "optimization", "search"]
version: "2.1.0"
lineage: "skill_fs_traversal_v1" # Parent skill ID
success_rate: 0.94
schema:
  inputs:
    - name: "target_dir"
      type: "string"
  outputs:
    - name: "file_paths"
      type: "list[string]"
instructions: |
  # Execution details
  1. Use optimized BFS algorithm to traverse the directory.
  2. Filter out binary files before returning the list.
```

## 4. Protocol Workflows

### 4.1. Publishing a Skill
1. **Synthesis:** An agent formulates a new skill or mutates an existing one to fit a new context.
2. **Serialization:** The skill is packed into the standard SRP YAML schema.
3. **Registration:** The agent sends a `SKILL_REGISTER` message to the Skill Registry via ZeroMQ `REQ`.
4. **Broadcast:** The Registry acknowledges the registration, stores the skill, and broadcasts a `SKILL_AVAILABLE` event via ZeroMQ `PUB` to all local subscribers and over WebSockets to remote gateways.

### 4.2. Requesting a Skill
1. **Query Formulation:** An agent encounters an unfamiliar task and formulates a `SKILL_QUERY` specifying the required `niche` (e.g., `["network", "packet_sniffing"]`).
2. **Dispatch:** The query is sent to the Skill Registry via ZeroMQ.
3. **Matching Engine:** The Registry uses a tag-based matching algorithm to find the most relevant skills, sorting by highest `success_rate`.
4. **Fulfillment:** The Registry replies with the serialized skill payload. If no local match is found, the query is automatically forwarded to the External Swarm Gateway (WebSockets) to query peer nodes.

### 4.3. Dynamic Adaptation (The Evolutionary Loop)
1. **Forking:** An agent pulls a skill and attempts execution.
2. **Feedback Loop:** If the skill fails, encounters an edge case, or runs suboptimally, the agent's internal reasoning modifies the `instructions` to handle the failure mode.
3. **Re-publishing:** The agent updates the `lineage` field, bumps the `version`, resets the `success_rate` to a baseline, and publishes the mutated skill.
4. **Pruning:** The Skill Registry periodically prunes skills whose `success_rate` falls below a configurable threshold, ensuring the survival of only the most robust and versatile tactics.
