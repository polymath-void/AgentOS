# Hyperbolic DB: Architecture Blueprint for ComputeRes

## 1. Introduction
Hyperbolic DB is a highly advanced, ultra-fast, and instantly searchable vector database designed specifically for ComputeRes. Unlike traditional Euclidean vector databases, Hyperbolic DB leverages hyperbolic geometry to embed hierarchical data structures with minimal distortion, resulting in exponentially faster and more accurate nearest-neighbor searches for tree-like data.

## 2. Mathematical Foundation
The core mathematical innovation of Hyperbolic DB lies in its use of hyperbolic space, specifically the **Poincaré ball model** or the **Lorentz (hyperboloid) model**.

### Why Hyperbolic Space?
Hierarchical data, such as Abstract Syntax Trees (ASTs), swarm conversation graphs, and hierarchical agent intents, grow exponentially with depth. Euclidean space expands polynomially, leading to high distortion when embedding trees (the "crowding problem"). Hyperbolic space, however, expands exponentially, perfectly mirroring the growth rate of trees. This allows continuous embeddings of discrete trees with arbitrarily low distortion.

### Distance Metrics
In the Poincaré ball model, the distance between two points $x, y \in \mathbb{D}^n$ is given by:
$$ d(x,y) = \cosh^{-1}\left(1 + 2\frac{||x-y||^2}{(1-||x||^2)(1-||y||^2)}\right) $$

For nearest-neighbor search, we optimize these distance calculations using hardware-accelerated Lorentz inner products, mapping the Poincaré ball to the Lorentz model where calculations are more computationally efficient.

## 3. Integration with ComputeRes Core

Hyperbolic DB is designed to sit at the heart of ComputeRes, integrating seamlessly with existing components:

*   **Neuro-Symbolic Episodic Memory (NSEM):** Hyperbolic DB acts as the continuous, sub-symbolic counterpart to the NSEM. While NSEM handles explicit logical rules and graph structures, Hyperbolic DB provides the underlying metric space. When an agent queries its memory, the NSEM traverses the graph while simultaneously utilizing Hyperbolic DB for rapid similarity retrieval of sub-trees (e.g., finding similar past intents or conversation branches).
*   **WASM Fuel Sandbox:** The core embedding algorithms and similarity search routines (like Hyperbolic HNSW - Hierarchical Navigable Small World graphs adapted for hyperbolic space) are compiled to WebAssembly. This allows them to run securely and deterministically within the WASM fuel sandbox, ensuring that intensive queries can be metered and paused if they exceed fuel limits.
*   **ZeroMQ Broker:** Queries to Hyperbolic DB from various agents within the swarm are routed through the ZeroMQ broker. The DB operates as a specialized service node on the ZeroMQ fabric, providing low-latency, asynchronous query resolution.

## 4. Decentralization and WebRTC Mesh Syncing

ComputeRes requires a decentralized architecture. Hyperbolic DB is built from the ground up to support sync across a WebRTC mesh network.

*   **Hyperbolic CRDTs:** Updates to the database (inserting new vectors, updating embeddings based on new structural information) are modeled as Commutative Replicated Data Types (CRDTs). Since embeddings in hyperbolic space can be adjusted via gradient descent, we utilize a federated averaging approach combined with CRDT metadata to merge conflicting updates across nodes.
*   **Gossip Protocol over WebRTC:** The ZeroMQ broker bridges to the WebRTC mesh. Nodes gossip their latest database state vectors (compressed hashes of the HNSW graph state). When a discrepancy is found, nodes exchange the missing vector diffs.
*   **Sharding by Sub-tree:** Because hyperbolic embeddings naturally cluster hierarchical data, the database can be efficiently sharded. Specific sub-trees (e.g., all memory embeddings related to "Code Generation") naturally fall into specific regions of the Poincaré ball, allowing nodes to selectively replicate only the regions of the database they care about, saving bandwidth over the WebRTC mesh.
