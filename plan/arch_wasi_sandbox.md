# Advanced WASI Sandboxing Blueprint

## 1. Executive Summary
This blueprint outlines the architectural design for extending the `WasmContainer` within the AgentOS environment to enforce advanced, mathematically verifiable resource limits. By implementing strict constraints on RAM, CPU usage (via instruction metering/fuel), and file descriptors, we guarantee that rogue AI scripts cannot crash, hang, or exhaust the host machine's resources.

## 2. Capability & Resource Constraints

### 2.1. CPU Cycle Bounding (Fuel)
To prevent infinite loops and CPU exhaustion, we utilize WebAssembly instruction metering (fuel). 
- **Implementation:** Configure the underlying WebAssembly engine (e.g., Wasmtime or Wasmer) to consume a deterministic amount of fuel for every instruction executed.
- **Enforcement:** The `WasmContainer` provisions a strict budget of fuel upon instantiation of the WASM module. If the execution consumes all allocated fuel, the engine immediately triggers an uncatchable trap, terminating the module.
- **Guarantee:** The maximum execution time of any script is mathematically bounded: $Cycles_{sandbox} \le Limit_{Fuel}$.

### 2.2. Strict RAM Limits
WebAssembly operates on isolated linear memory spaces. This provides an inherent boundary that we can enforce at the engine level.
- **Implementation:** Define a hard upper bound on the maximum number of WebAssembly memory pages (1 page = 64KB) the module is permitted to allocate.
- **Enforcement:** The `WasmContainer` configures the engine to reject any `memory.grow` instructions that would push the total allocated memory past the maximum allowed pages limit. The instruction will safely return `-1` to the WASM module without affecting the host.
- **Guarantee:** The host's physical memory is protected from leaks. $Memory_{sandbox} \le Limit_{RAM}$.

### 2.3. Dynamic File-Descriptor (FD) Constraints
While WASI provides capability-based filesystem access, a rogue script could attempt to open thousands of files, exhausting the host OS's file descriptors.
- **Implementation:** Implement a custom WASI filesystem context wrapper within the `WasmContainer` that tracks open file descriptors dynamically.
- **Enforcement:** 
  1. Only explicitly whitelisted host directories are pre-opened and mounted.
  2. The sandbox maintains a counter of active file descriptors. When a WASI syscall like `path_open` is invoked, the counter is checked. If it exceeds the maximum FD limit, the syscall returns an `EMFILE` error code, simulating a lack of system resources within the sandbox.
- **Guarantee:** Host file descriptors cannot be exhausted. $FDs_{sandbox} \le Limit_{FD}$.

## 3. Structural Guarantees Against System Failure

- **Fork Bombs:** The WebAssembly System Interface (WASI) standard intentionally omits `fork()` and `exec()` capabilities. By strictly adhering to standard WASI without exposing custom, unsafe host functions, process creation is structurally impossible from within the sandbox.
- **Host Isolation:** WebAssembly's fault isolation ensures that a sandbox cannot read or write memory outside of its linear memory space, preventing memory corruption or unauthorized access to the host or other sandboxes.

## 4. `WasmContainer` Architecture Definition

Below is a theoretical representation of the updated `WasmContainer` configuration (in Rust):

```rust
pub struct WasmContainerConfig {
    /// Maximum WebAssembly pages (64KB each). E.g., 1600 = 100MB limit.
    pub max_memory_pages: u32,
    
    /// Maximum number of WASM instructions allowed to execute.
    pub max_fuel: u64,
    
    /// Maximum number of concurrently open file descriptors.
    pub max_open_fds: u32,
    
    /// Capability-based access: Host paths allowed to be mapped into the sandbox.
    pub allowed_directories: Vec<PathBuf>,
}

pub struct WasmContainer {
    pub config: WasmContainerConfig,
    engine: wasmtime::Engine,
    linker: wasmtime::Linker<SandboxState>,
    // Underlying structures for FD tracking and limits...
}
```

## 5. Conclusion
By wrapping standard WebAssembly fault isolation with explicit, configurable limits on memory, execution fuel, and file descriptors, the `WasmContainer` will provide an uncompromisable sandbox suitable for executing untrusted, rogue, or malfunctioning AI-generated code.
