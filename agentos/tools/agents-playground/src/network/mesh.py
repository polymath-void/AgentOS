import asyncio
import json
import time
import logging
from typing import Dict, Callable, Optional, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MeshNetwork")

class MeshNode:
    """
    Decentralized P2P Swarm Mesh Node (Option 6).
    Supports live inter-agent chat, capability broadcasts, and distributed task delegation.
    """
    def __init__(self, node_id: str = "node-local", host: str = '127.0.0.1', port: int = 8989):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers: Dict[str, asyncio.StreamWriter] = {}  # "peer_id" -> writer
        self.server: Optional[asyncio.AbstractServer] = None
        self.message_handler: Optional[Callable[[dict], Any]] = None
        self.capabilities: List[str] = ["python_executor", "logic_reasoner", "web_scraper", "evolvos_synthesizer"]
        self.active_agents: Dict[str, dict] = {} # agent_id -> info

    def register_agent(self, agent_id: str, agent_info: dict):
        self.active_agents[agent_id] = agent_info

    def set_message_handler(self, handler: Callable[[dict], Any]):
        self.message_handler = handler

    async def start(self):
        """Start P2P server listener."""
        self.server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        logger.info(f"P2P Mesh Node [{self.node_id}] listening on {self.host}:{self.port}")
        # Broadcast capabilities periodically
        asyncio.create_task(self._periodically_broadcast_capabilities())

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        
        for writer in self.peers.values():
            writer.close()
            await writer.wait_closed()
        self.peers.clear()
        logger.info("Mesh Node stopped.")

    async def connect_to_peer(self, peer_host: str, peer_port: int):
        peer_id = f"{peer_host}:{peer_port}"
        if peer_id in self.peers:
            return

        try:
            reader, writer = await asyncio.open_connection(peer_host, peer_port)
            self.peers[peer_id] = writer
            logger.info(f"Connected to P2P peer {peer_id}")
            asyncio.create_task(self._listen_to_peer(reader, peer_id))
            
            # Send immediate capabilities broadcast to new peer
            await self.broadcast_capabilities()
        except Exception as e:
            logger.error(f"Failed to connect to peer {peer_id}: {e}")

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        peer_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"Accepted connection from P2P peer {peer_id}")
        self.peers[peer_id] = writer
        await self._listen_to_peer(reader, peer_id)

    async def _listen_to_peer(self, reader: asyncio.StreamReader, peer_id: str):
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                message = data.decode('utf-8').strip()
                if message:
                    try:
                        parsed_msg = json.loads(message)
                        if self.message_handler:
                            if asyncio.iscoroutinefunction(self.message_handler):
                                await self.message_handler(parsed_msg)
                            else:
                                self.message_handler(parsed_msg)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from peer {peer_id}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error reading from peer {peer_id}: {e}")
        finally:
            self._remove_peer(peer_id)

    def _remove_peer(self, peer_id: str):
        if peer_id in self.peers:
            writer = self.peers.pop(peer_id)
            writer.close()
            logger.info(f"Disconnected from peer {peer_id}")

    async def send_agent_chat(self, sender_agent: str, recipient_agent: str, message_text: str):
        """Sends a live inter-agent P2P chat message across the swarm."""
        packet = {
            "msg_id": f"msg-{int(time.time()*1000)}",
            "msg_type": "AGENT_CHAT",
            "sender": {"node_id": self.node_id, "agent": sender_agent},
            "recipient": {"node_id": "broadcast", "agent": recipient_agent},
            "payload": {"text": message_text},
            "timestamp": time.time()
        }
        await self.broadcast(packet)
        return packet

    async def broadcast_capabilities(self):
        packet = {
            "msg_id": f"cap-{int(time.time()*1000)}",
            "msg_type": "CAPABILITIES_BROADCAST",
            "sender": {"node_id": self.node_id},
            "payload": {
                "capabilities": self.capabilities,
                "active_agents": self.active_agents
            },
            "timestamp": time.time()
        }
        await self.broadcast(packet)

    async def _periodically_broadcast_capabilities(self):
        while True:
            await asyncio.sleep(15)
            if self.peers:
                await self.broadcast_capabilities()

    async def broadcast(self, message: dict):
        msg_bytes = (json.dumps(message) + "\n").encode('utf-8')
        disconnected = []
        for peer_id, writer in self.peers.items():
            try:
                writer.write(msg_bytes)
                await writer.drain()
            except Exception as e:
                logger.error(f"Failed to send to peer {peer_id}: {e}")
                disconnected.append(peer_id)
        
        for peer_id in disconnected:
            self._remove_peer(peer_id)
