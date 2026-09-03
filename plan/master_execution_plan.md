# First Breath Simulation: Master Execution Plan

## 1. Architectural Synthesis: The Intertwined Engine

The "First Breath Simulation" is the critical milestone where ComputeRes transcends from theory to a living, decentralized, secure execution environment. This simulation integrates the three core pillars:

1.  **ZeroMQ IPC Broker (The Local Nervous System):** Acts as the high-throughput, low-latency backbone for intra-node communication. It routes messages between the WebRTC router, the MCP Gateway, and the local WASM execution engines.
2.  **WebRTC Mesh (The Global Nervous System):** Connects disparate edge nodes into a unified computing substrate. It relies on CRDTs for state synchronization and routes requests for distributed tool execution.
3.  **WASM/WASI Swarm Consensus Oracle (The Immune System & Sandboxing):** Wraps all dynamic tool executions in hermetically sealed WASM containers. When a container requests elevated privileges, execution halts, and the Oracle coordinates a swarm-wide vote (propagated via ZeroMQ to the WebRTC mesh) to dynamically grant or deny WASI capabilities.

**The Execution Loop:**
An external agent issues a tool request via the **MCP Gateway** -> The request is routed via **ZeroMQ** to the target node's **WebRTC Router** (if remote) or local executor -> The tool is instantiated inside a **WASM/WASI Container** -> If the tool needs restricted access (e.g., file write), it pauses -> The **Swarm Oracle** broadcasts a consensus request via **ZeroMQ** -> **WebRTC** to other nodes -> Nodes deliberate and vote via CRDT updates -> Upon supermajority, **ZeroMQ** triggers the local Oracle to inject the capability -> WASM execution resumes and returns the result back up the chain.

---

## 2. Target File Modifications & Structure

The codebase will be structured to isolate these three pillars while providing a unified `main.py` entry point.

### New/Modified Files:
-   `src/core/broker.py`: ZeroMQ ROUTER/DEALER IPC logic.
-   `src/network/mesh.py`: WebRTC DataChannel management and CRDT state sync.
-   `src/sandbox/wasm_engine.py`: WASM host environment and WASI capability management.
-   `src/oracle/consensus.py`: Swarm consensus voting logic.
-   `src/gateway/mcp_server.py`: MCP to ZeroMQ translation layer.
-   `tests/test_first_breath.py`: The simulation test suite.

---

## 3. Core Class Structures

### `src/core/broker.py`
```python
class IPCBroker:
    def __init__(self, router_bind_addr, dealer_bind_addr):
        # Initializes ZeroMQ context, ROUTER socket (front), DEALER socket (back)
        pass
        
    async def start(self):
        # Async loop to proxy messages between Gateway/Mesh and Workers
        pass
```

### `src/network/mesh.py`
```python
class WebRTCMeshRouter:
    def __init__(self, node_id, zmq_pub_socket, zmq_sub_socket):
        self.node_id = node_id
        self.peers = {} # Connected WebRTC peers
        self.crdt_state = CRDTManager()
        
    async def broadcast_state_update(self, update):
        # Send CRDT update over all WebRTC DataChannels
        pass
        
    async def listen_ipc(self):
        # Subscribe to local ZeroMQ for outbound mesh messages
        pass
```

### `src/sandbox/wasm_engine.py`
```python
class WasmContainer:
    def __init__(self, wasm_binary, initial_capabilities):
        # Initialize Wasmtime/Wasmer runtime with WASI configuration
        self.runtime = WasmRuntime()
        self.capabilities = initial_capabilities
        
    def execute(self, func_name, args):
        # Start execution; trap capability requests
        pass
        
    def inject_capability(self, capability):
        # Dynamically map new host directories/sockets to WASI
        pass
```

### `src/oracle/consensus.py`
```python
class SwarmOracle:
    def __init__(self, node_id, ipc_socket):
        self.node_id = node_id
        self.active_votes = {} # UUID -> VoteState
        
    async def request_capability(self, tool_id, capability):
        # Pause WASM execution, generate Vote UUID
        # Publish request to ZeroMQ -> WebRTC
        pass
        
    def process_vote(self, vote_crdt):
        # Tally votes. If supermajority (>75%), signal WASM engine to resume
        pass
```

---

## 4. Step-by-Step Execution Plan

### Phase 1: Local IPC and Gateway Foundation
1.  **Implement `IPCBroker`**: Set up the ZeroMQ `ROUTER/DEALER` device.
2.  **Implement `MCPGateway`**: Map incoming JSON-RPC requests to ZeroMQ multipart frames.
3.  **Test**: Verify a dummy MCP request flows through the Broker and returns an ACK.

### Phase 2: WebRTC Mesh & CRDT State
1.  **Implement `WebRTCMeshRouter`**: Create signaling handshake and DataChannel establishment using `aiortc`.
2.  **CRDT Integration**: Implement a basic CRDT (e.g., LWW-Element-Set) for shared state.
3.  **IPC Bridge**: Connect the Mesh Router to the ZeroMQ Broker.
4.  **Test**: Spin up two local node instances. Verify a state change on Node A propagates over WebRTC and triggers a ZeroMQ PUB event on Node B.

### Phase 3: WASM/WASI Sandboxing
1.  **WASM Runtime Integration**: Integrate `wasmtime-py`.
2.  **Containerize Execution**: Build the `WasmContainer` class to load compiled `.wasm` tools.
3.  **WASI Enforcement**: Configure default denial of filesystem/network access.
4.  **Test**: Attempt to write a file from inside the WASM container and ensure it traps with a permission error.

### Phase 4: Swarm Consensus Oracle
1.  **Voting Logic**: Implement the `SwarmOracle` state machine.
2.  **Capability Injection**: Add logic to pause a trapped WASM execution, wait for a resolved vote, and update the WASI context dynamically.
3.  **Test**: Simulate a capability request, inject synthetic votes, and verify the WASM container resumes execution successfully.

---

## 5. The "First Breath Simulation" Testing Logic

The capstone test (`tests/test_first_breath.py`) will orchestrate the full stack in a simulated multi-node environment.

**Simulation Steps:**
1.  **Bootstrapping**: Spin up three logical nodes in separate processes: Node A (Gateway), Node B (Edge Worker 1), Node C (Security Agent/Oracle). They connect via WebRTC.
2.  **Invocation**: An external test script (acting as an MCP Agent) sends an `execute_tool` request to Node A via MCP. The request is `write_distributed_log(msg="First Breath")`.
3.  **Routing**: Node A determines the log tool resides on Node B. Node A serializes the request and routes it via ZeroMQ -> WebRTC -> Node B.
4.  **Sandboxing**: Node B receives the request via WebRTC -> ZeroMQ. It instantiates the `write_distributed_log` WASM container.
5.  **Trap & Request**: The WASM container attempts to open `/logs/first_breath.txt`. The WASI engine denies it and traps. Node B's `SwarmOracle` creates a Capability Request for `file_write:/logs/` and broadcasts it over WebRTC.
6.  **Consensus**: Node A and Node C receive the request. Node C (simulating a security agent) verifies the request logic and broadcasts an "Approve" vote via CRDT. Node A also votes "Approve".
7.  **Resolution**: Node B receives the votes. The CRDT tallies a 100% supermajority. Node B's `SwarmOracle` signals the local `WasmContainer`.
8.  **Injection & Completion**: Node B dynamically maps the `/logs` capability into the paused WASI environment. Execution resumes, the file is written, and the success response bubbles back through ZeroMQ -> WebRTC -> Node A -> MCP Agent.

This simulation proves the end-to-end viability of the ComputeRes architecture.
