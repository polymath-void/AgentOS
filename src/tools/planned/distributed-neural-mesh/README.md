# Distributed Neural Mesh

## Overview
A simulated, asynchronous mesh network for distributed task processing and encrypted data transfer.

## Features
- **Master Orchestrator**: Splits tasks into chunks and dispatches them across the mesh.
- **Node Workers**: Daemon threads that asynchronously process tasks from a centralized queue.
- **Payload Encryption**: All chunks are encrypted before transit using XOR and Base64 algorithms.
- **Automatic Reassembly**: Orchestrator waits for all nodes to complete and reconstructs the final output.

## Usage
```bash
python3 main.py
```
