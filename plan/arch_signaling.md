# AgentOS WebRTC Signaling Architecture Blueprint

## 1. Overview
The AgentOS WebRTC Mesh requires a robust and lightweight Signaling Layer to negotiate peer-to-peer (P2P) connections between autonomous agents. This Signaling Server facilitates Swarm Matchmaking, NAT Traversal (STUN/TURN), and the exchange of Session Description Protocol (SDP) and ICE candidates. 

Crucially, to maintain a truly decentralized architecture, the Signaling Server is designed to **drop out** of the communication loop the moment a P2P WebRTC `DataChannel` is successfully established.

## 2. Signaling Server Architecture
**Technology Stack:** Python, `asyncio`, and `websockets` (or FastAPI with WebSockets).

### 2.1 Core Responsibilities
1.  **Swarm Matchmaking:** Agents connect to the Signaling Server and declare a `swarm_id`. The server groups connections by `swarm_id` and notifies peers of new joiners.
2.  **NAT Traversal (STUN/TURN):** Upon connection, the server provides agents with a list of active STUN/TURN servers (e.g., Google's public STUN, or a self-hosted Coturn instance) to handle complex NAT topologies.
3.  **SDP & ICE Exchange:** The server acts as a transient message relay for `offer`, `answer`, and `ice-candidate` payloads between peers.
4.  **Ephemeral Lifecycle:** The server does not handle any AgentOS payload data. It exists solely to bootstrap the WebRTC `RTCPeerConnection`.

### 2.2 Signaling Protocol (JSON over WebSockets)
*   **Join Swarm:** `{"type": "join", "node_id": "agent-1", "swarm_id": "alpha-squad"}`
*   **Swarm Roster Update (Server -> Client):** `{"type": "roster", "peers": ["agent-2", "agent-3"], "ice_servers": [{"urls": "stun:stun.l.google.com:19302"}]}`
*   **SDP Offer/Answer:** `{"type": "offer", "target": "agent-2", "sdp": "..."}`
*   **ICE Candidate:** `{"type": "ice-candidate", "target": "agent-2", "candidate": "..."}`

## 3. Integration with `mesh.py` (`WebRTCMeshRouter`)

The existing `WebRTCMeshRouter` in `mesh.py` bridges the local ZeroMQ IPC broker to the decentralized WebRTC mesh. We will augment it to handle signaling and P2P lifecycle management using `aiortc` and `websockets`.

### 3.1 Step-by-Step Connection Flow
1.  **Initialization:** `WebRTCMeshRouter` connects to the ZeroMQ pub/sub sockets (already implemented).
2.  **Signaling Connection:** `WebRTCMeshRouter` opens a WebSocket connection to the Signaling Server and sends a `join` message with its `node_id` and `swarm_id`.
3.  **Peer Discovery:** Upon receiving the swarm roster, the router initializes an `aiortc.RTCPeerConnection` for each peer.
4.  **Negotiation:**
    *   The router creates a WebRTC `RTCDataChannel` (e.g., named "agentos-mesh").
    *   It generates an SDP Offer and sends it via the WebSocket.
    *   Peers respond with SDP Answers and ICE candidates.
5.  **P2P DataChannel Establishment:** The ICE gathering process completes, and the P2P connection punches through the NAT.
6.  **Signaling Dropout:** Once the `RTCDataChannel` fires the `on_open` event (indicating a successful P2P link), the `WebRTCMeshRouter` **closes its WebSocket connection** to the Signaling Server. 

### 3.2 Augmenting `mesh.py`
To support this blueprint, `WebRTCMeshRouter` requires the following additions:
*   A `_connect_signaling()` async loop to handle the WebSocket lifecycle.
*   An `aiortc.RTCPeerConnection` dictionary mapping `peer_node_id` -> `RTCPeerConnection`.
*   WebRTC DataChannel event listeners (`@channel.on("message")`) that deserialize incoming P2P messages and route them to the ZeroMQ `pub_socket`, bridging the remote P2P mesh into the local kernel IPC.
*   Updating `_zmq_to_webrtc_loop()` to iterate over active `RTCDataChannel` instances and broadcast local ZeroMQ events directly to peers.

## 4. NAT Traversal & Resiliency
*   **ICE Servers:** The Signaling Server should dynamically dispense STUN/TURN credentials. For production, a Coturn TURN server is highly recommended to guarantee connectivity when symmetric NATs block direct STUN traversal.
*   **Reconnection Logic:** If the WebRTC `DataChannel` state changes to `closed` or `failed`, the `WebRTCMeshRouter` must wake up, reconnect to the Signaling Server, and renegotiate a new P2P connection.

## 5. Summary
By decoupling the signaling from the actual data transmission, AgentOS achieves true decentralization. The Signaling Server is merely an ephemeral matchmaker. Once agents discover each other, they share state via the `CRDTManager` over direct WebRTC DataChannels, leaving no single point of failure in the active Swarm.
