# Neural Agent Network Architecture

This document details the core architectural components of the Neural Agent Network engine.

## Core Components

### 1. P2P Mesh
The **P2P Mesh** provides the communication backbone for the network.
- **Decentralized**: Agents can discover and communicate with each other without relying on a central server.
- **Robustness**: The mesh topology ensures that communication remains stable even if individual nodes go offline.
- **Protocol**: Utilizes lightweight, efficient protocols for message serialization and transmission.

### 2. Episodic Memory
The **Episodic Memory** system allows agents to maintain state and learn from past experiences.
- **Event Logging**: Agents record key interactions, decisions, and outcomes.
- **Retrieval**: Agents can query their memory to inform future actions based on historical context.
- **Storage**: Designed to efficiently handle time-series data and complex relationships between events.

### 3. WASM Actors
**WASM (WebAssembly) Actors** serve as the execution environments for agent logic.
- **Isolation**: Each agent runs in a sandboxed WASM environment, ensuring security and stability.
- **Portability**: Agent logic can be written in any language that compiles to WebAssembly.
- **Performance**: WASM provides near-native execution speed, making it ideal for running complex agent behaviors.

## System Interaction

The WASM Actors contain the decision-making logic of the agents. When an agent needs to communicate, it sends a message through the P2P Mesh. Simultaneously, the agent logs significant events to its Episodic Memory. When faced with a new situation, the WASM Actor queries the Episodic Memory and uses the retrieved context to formulate a response or action, which may then be broadcast over the P2P Mesh.
