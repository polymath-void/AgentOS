# Agent OS Hub - Architecture

This hub acts as the central orchestrator for the multi-agent swarm, integrating the Polymath recursive reasoning protocols with the Nano Neural Mesh connectivity layer.

## Core Modules
- **`factory/`**: Knowledge-gated deployment of sub-agents using blueprints from `config/blueprints`.
- **`orchestrator/`**: Authentication via Polymath bridges and validation via `tests/harness`.
- **`src/`**: Shared utilities, including the `MeshInterface` shim.

## Integration Principles
1. **Recursive Instantiation**: Use the factory to spawn sub-agents based on Polymath tiers.
2. **Knowledge Grafting**: Inject restricted `Knowledge Objects` during sub-agent initialization.
3. **Safety First**: Every deployment must pass the validation harness before mesh entry.
