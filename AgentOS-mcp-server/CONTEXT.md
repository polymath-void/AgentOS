# Agent-OS-Hub Context

## Overview
Centralized orchestrator for the **Polymath Reasoning Centre**, providing a unified swarm server hub.

## Core Architecture
- **Orchestrator (`main.py`, `core/dispatch/`)**: Dispatches tasks to sub-systems via `DispatchNetwork`.
- **Reasoning Plugins (`plugins/`)**: Dynamic, schema-registered capabilities (49+ tools) with mandatory simulation mirrors for safety.
- **Integration Layer**:
  - `nano-neural-mesh`: Fabric for swarm communication.
  - `agents-playground`: Sandbox for agent evolution.
  - `teamwork_projects`: Verification harness for E2E tests.

## Workflow Protocol
1. **Simulation Phase**: All tasks MUST be routed through the `simulate` mode (`DispatchNetwork` -> `plugins/mirrors/`) before actual execution.
2. **Dispatch Phase**: Only after verification in simulation can tasks proceed to `execute` mode.

## System Management
- Server runs as a unified background service.
- Plugins are registered dynamically via `register_tool`.
- Documentation and context are maintained per project mandates.
