# ComputeRes Decentralized AI Swarm Topology: Architectural Blueprint

## 1. Executive Summary

ComputeRes is an orchestration environment natively designed for external AI agents. Lacking an internal Large Language Model (LLM), ComputeRes exposes highly capable computing environments to external, specialized agents via the Model Context Protocol (MCP). The goal of the Decentralized AI Swarm Topology is to evolve the current primitive WebRTC and ZeroMQ IPC implementations into a seamless, multi-device mesh network. This allows a singular or multi-agent swarm to treat an array of edge nodes (laptops, phones, servers) as a cohesive computational substrate.

## 2. Core Tenets

- **MCP as the Universal Interface:** Every resource, file, database, and hardware sensor across the node mesh is projected through a centralized or decentralized MCP server layer.
- **Stateless Orchestration:** Agents interacting with the environment do not need to maintain node-specific state. The Swarm handles state reconciliation.
- **Zero-Trust & Peer-to-Peer:** Nodes communicate via WebRTC (DataChannels for arbitrary binary data and events), utilizing NAT traversal techniques (STUN/TURN) without relying on a central relay server for throughput.
- **Local Inter-Process Communication (IPC):** ZeroMQ handles high-throughput, low-latency IPC for components existing on the same physical node.

## 3. Network Topology & WebRTC Mesh

### 3.1 WebRTC DataChannels for the Edge
The Swarm is constructed as an unstructured peer-to-peer mesh. When a new edge node (e.g., a phone) comes online, it performs a brief signaling handshake (using a lightweight signaling server or an existing node) to exchange WebRTC SDP offers/answers. Once connected, a full-duplex, encrypted SCTP-based DataChannel is established. 

### 3.2 Signaling and Discovery
- **Bootstrapping:** New nodes connect to a known bootstrap node (e.g., the primary laptop).
- **Gossip Protocol:** Node discovery and status updates propagate via an epidemic (gossip) protocol running over the WebRTC channels. This ensures every node maintains a routing table of the global Swarm topology.
- **NAT Traversal:** ICE (Interactive Connectivity Establishment) ensures connectivity across restrictive firewalls and mobile networks.

## 4. MCP Aggregation and Orchestration

How does a single MCP agent orchestrate tasks across multiple devices?

### 4.1 The Virtualized MCP Server
The agent connects to a single entry point (the **Gateway Node**). This Gateway runs the Virtualized MCP Server. It acts as a reverse proxy, aggregating the MCP resources (Prompts, Tools, Resources) of all connected edge nodes.

### 4.2 Resource Addressing (URNs)
Resources across the Swarm are addressed using Universal Resource Names that encapsulate the Node ID:
`mcp://<node-id>/<resource-type>/<resource-id>`
e.g., `mcp://phone-01/sensors/gps` or `mcp://laptop-xyz/files/workspace`.

### 4.3 Distributed Tool Execution
When the MCP Agent invokes a tool, the Gateway Node inspects the request. If the tool is designated for a remote node (e.g., "capture photo on phone"), the Gateway serializes the JSON-RPC request and routes it via the WebRTC DataChannel to the target node. The remote node executes the tool, retrieves the output (e.g., base64 image), and routes the JSON-RPC response back over WebRTC.

## 5. State Synchronization and Reconciliation

State synchronization across a distributed mesh without a central database requires strong eventual consistency.

### 5.1 Conflict-Free Replicated Data Types (CRDTs)
The Swarm state (e.g., list of active nodes, shared memory blocks, distributed file pointers, task queues) is modeled using CRDTs (specifically, state-based and operation-based CRDTs).
- **Why?** CRDTs allow any node to update local state immediately. Updates are broadcasted via the WebRTC gossip protocol. Concurrent updates mathematically resolve without conflicts, ensuring identical state across the Swarm.

### 5.2 ZeroMQ IPC Bus (Intra-Node)
On a single physical device, the ComputeRes daemon, the WebRTC mesh router, and the local MCP resource handlers communicate via ZeroMQ `REQ/REP` and `PUB/SUB` sockets. 
- The **WebRTC Router** receives a CRDT state update from a remote node.
- It publishes the update on a local ZeroMQ `PUB` socket.
- The **Local State Manager** subscribes to this update, merges the CRDT, and updates the local representation.

## 6. Security and Authentication

- **Agent Possession:** Agents must authenticate with the Gateway Node using mutual TLS (mTLS) or a capability-based token system before they can access the Virtualized MCP Server.
- **Node Trust:** Edge nodes verify each other's identity using asymmetric cryptography. A shared root certificate or a decentralized Web of Trust ensures rogue nodes cannot join the Swarm and spoof state.

## 7. Execution Flow: A Practical Example

1. **Agent Request:** The external LLM agent connects to the Laptop (Gateway) via MCP and requests: "Analyze the dataset on the laptop, and send an SMS alert via the phone if anomalies are found."
2. **Analysis:** The agent uses local tools on the laptop (via ZeroMQ IPC) to process the dataset.
3. **Trigger:** An anomaly is found. The agent invokes the `send_sms` tool, which is exposed by the Gateway but actually belongs to `phone-01`.
4. **Routing:** The Gateway routes the JSON-RPC tool invocation over the WebRTC DataChannel to `phone-01`.
5. **Execution:** `phone-01` receives the request, utilizes local Android APIs to send the SMS, and returns a success response over WebRTC.
6. **Completion:** The Gateway relays the success message back to the MCP agent.

## 8. Future Milestones
- Introduce WebAssembly (Wasm) runtime on edge nodes to allow agents to deploy persistent, sandboxed background tasks across the Swarm.
- Migrate to WebTransport to complement WebRTC for massive data streams (e.g., raw video feeds from phones to laptops).
