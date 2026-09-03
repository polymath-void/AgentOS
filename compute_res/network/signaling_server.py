import asyncio
import json
import logging
import websockets
from collections import defaultdict
import os

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] SignalingServer: %(message)s')
logger = logging.getLogger("Signaling")

# Maps swarm_id -> dict(node_id -> websocket)
swarms = defaultdict(dict)

async def handle_client(websocket):
    """Handles incoming WebSocket connections and routes P2P negotiation packets."""
    node_id = None
    swarm_id = None
    
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "join":
                node_id = data.get("node_id")
                swarm_id = data.get("swarm_id")
                
                if not node_id or not swarm_id:
                    logger.error("Invalid join request. Missing node_id or swarm_id.")
                    continue
                    
                swarms[swarm_id][node_id] = websocket
                logger.info(f"Node {node_id} joined swarm {swarm_id}. Total peers in swarm: {len(swarms[swarm_id])}")
                
                # Send the roster (list of other peers) to the new joiner
                roster = [peer for peer in swarms[swarm_id].keys() if peer != node_id]
                roster_msg = {
                    "type": "roster",
                    "peers": roster,
                    "ice_servers": [{"urls": "stun:stun.l.google.com:19302"}] # Public STUN for traversal
                }
                await websocket.send(json.dumps(roster_msg))
                
                # Notify existing peers that a new node joined
                for peer_id, peer_ws in swarms[swarm_id].items():
                    if peer_id != node_id:
                        await peer_ws.send(json.dumps({"type": "peer_joined", "peer_id": node_id}))
                        
            elif msg_type in ("offer", "answer", "ice-candidate"):
                target = data.get("target")
                if not target or target not in swarms[swarm_id]:
                    logger.warning(f"Failed to route {msg_type}: Target {target} not found in swarm {swarm_id}.")
                    continue
                
                # Route the signaling payload directly to the target node
                target_ws = swarms[swarm_id][target]
                await target_ws.send(json.dumps(data))
                logger.debug(f"Routed {msg_type} from {node_id} to {target}")

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"WebSocket connection closed for node {node_id}")
    except Exception as e:
        logger.error(f"Error handling client {node_id}: {e}")
    finally:
        # Cleanup when a node disconnects (or executes the "Dropout" strategy)
        if swarm_id and node_id in swarms[swarm_id]:
            del swarms[swarm_id][node_id]
            logger.info(f"Node {node_id} removed from swarm {swarm_id}.")
            if not swarms[swarm_id]:
                del swarms[swarm_id]

async def start_signaling_server(host="0.0.0.0", port=8765):
    """Boots the WebSocket server."""
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"Signaling Server Matchmaker running on ws://{host}:{port}")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(start_signaling_server())
    except KeyboardInterrupt:
        logger.info("Signaling Server shutdown.")
