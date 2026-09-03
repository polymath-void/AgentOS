# Agent Swarm: Tasks & Reasoning

This document contains context-free execution prompts mapped to identity tags. Any micro-agent can consume a tag and execute the task perfectly without needing global context.

---

### `[NANO-01:CONFIG]`
- **Role**: Configuration Specialist
- **Reasoning Prompt**: Write `core/config.py`. Set up a robust Python logger named `NanoMesh` that outputs to the console with timestamps. Define a `Settings` class to hold default mesh network parameters.
- **Skills**: Python, Standard Logging.

### `[NANO-02:MESH_P2P]`
- **Role**: Network Architect
- **Reasoning Prompt**: Write `core/mesh.py`. Implement a `NeuralMesh` class that maintains a dictionary of connected node instances. Provide a `broadcast(sender_id, message)` function that iterates through all nodes and routes the message to everyone except the sender, simulating a decentralized P2P synapse link.
- **Skills**: Python, Distributed Networking Logic.

### `[NANO-03:WASM_ENG]`
- **Role**: WASM Integration Engineer
- **Reasoning Prompt**: Write `core/engine.py`. Create a `WasmEngine` class. It must import the `wasmtime` library, initialize an `Engine` and a `Store`, and provide a `load_module(filepath)` method that reads a `.wasm` file from disk and returns a compiled `wasmtime.Module`. Handle basic file-not-found exceptions gracefully.
- **Skills**: Python, Wasmtime API.

### `[NANO-04:SPAWNER]`
- **Role**: Optimization & Concurrency Expert
- **Reasoning Prompt**: Write `core/spawner.py`. Create a `NanoNodeSpawner` class. It should take a pre-loaded `wasmtime.Module` and the `Store`. Provide a `duplicate_node()` method that instantiates the module into a running instance. Log the execution time of the instantiation to prove it operates in the nanosecond/microsecond scale.
- **Skills**: Python, Wasmtime Instantiation, Performance Profiling.

### `[NANO-05:RUST_NODE]`
- **Role**: Systems Programmer
- **Reasoning Prompt**: Write `nodes/src/neural_processor.rs`. It must contain a `#[no_mangle]` extern "C" function named `process_signal(input: i32) -> i32` that executes core neural logic (e.g., multiplies the input by 2). Include an empty `main` function so it can be compiled as a WASI standalone payload.
- **Skills**: Rust, WebAssembly System Interface (WASI).

### `[NANO-06:INTEGRAT]`
- **Role**: Codebase-Integrator
- **Reasoning Prompt**: Write `main.py`. You are the final integrator. Import `NeuralMesh`, `WasmEngine`, and `NanoNodeSpawner`. Wire them together: Initialize the engine, load the wasm payload, spawn 10 duplicate nodes, attach them to the mesh, and trigger a test broadcast signal across the network.
- **Skills**: Python, Systems Integration, Architecture.
