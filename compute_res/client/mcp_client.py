import asyncio
import json
import uuid
import logging
import zmq
import zmq.asyncio
import os

os_path = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os_path, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] MCPClient: %(message)s')
logger = logging.getLogger("StandaloneClient")

class ComputeResClient:
    """
    The Decoupled Standalone Client.
    Allows ANY external LLM "Brain" to connect to the ComputeRes Gateway over standard TCP.
    It completely abstracts the ZeroMQ and WebRTC mesh complexities from the LLM.
    """
    def __init__(self, gateway_url="tcp://127.0.0.1:5557", capability_stream_url="tcp://127.0.0.1:5555"):
        self.context = zmq.asyncio.Context()
        
        # Connection to Gateway for sending JSON-RPC intents
        self.gateway_socket = self.context.socket(zmq.REQ)
        self.gateway_socket.setsockopt(zmq.RCVTIMEO, 10000) # 10s timeout
        self.gateway_socket.connect(gateway_url)
        
        # Subscribes to real-time capability (AST Tool) updates from the OS
        self.schema_socket = self.context.socket(zmq.SUB)
        self.schema_socket.connect(capability_stream_url)
        self.schema_socket.setsockopt_string(zmq.SUBSCRIBE, "SYS_CAPABILITY_UPDATE")
        
        self.available_tools = []

    async def poll_tool_schemas(self):
        """Runs in background. Updates local JSON Schema when ComputeRes evolves a new tool."""
        logger.info("Listening for dynamic AST capability updates from ComputeRes...")
        while True:
            try:
                topic_bytes, payload_bytes = await self.schema_socket.recv_multipart()
                payload = json.loads(payload_bytes.decode('utf-8'))
                
                # Update local tool registry for the LLM to read
                new_capabilities = payload.get("capabilities", [])
                self.available_tools.extend(new_capabilities)
                logger.info(f"ComputeRes Evolved New Tools. Client Schema updated: {[t['name'] for t in new_capabilities]}")
            except Exception as e:
                logger.error(f"Error polling schemas: {e}")

    async def execute_tool(self, tool_name: str, arguments: dict) -> str:
        """
        Formats an LLM's raw intent into strict JSON-RPC 2.0 and transmits to ComputeRes.
        """
        req_id = str(uuid.uuid4())
        rpc_request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        logger.info(f"Dispatching JSON-RPC Intent to Gateway: {tool_name}")
        await self.gateway_socket.send_json(rpc_request)
        
        try:
            reply = await self.gateway_socket.recv_json()
            return json.dumps(reply, indent=2)
        except zmq.error.Again:
            logger.error("ComputeRes Gateway timeout. Swarm may be running a heavy consensus protocol.")
            # Reconnect on timeout
            endpoint = self.gateway_socket.getsockopt_string(zmq.LAST_ENDPOINT)
            if not endpoint:
                endpoint = "tcp://127.0.0.1:5557"
            self.gateway_socket.close(linger=0)
            self.gateway_socket = self.context.socket(zmq.REQ)
            self.gateway_socket.setsockopt(zmq.RCVTIMEO, 10000)
            self.gateway_socket.connect(endpoint)
            return json.dumps({"error": "Gateway Timeout"})

# Example usage for an LLM:
# client = ComputeResClient()
# asyncio.create_task(client.poll_tool_schemas())
# result = await client.execute_tool("write_distributed_log", {"msg": "Hello Swarm"})
