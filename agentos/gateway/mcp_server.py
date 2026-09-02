import os
import json
import zmq
import zmq.asyncio
import asyncio
import logging

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] MCPGateway: %(message)s')
logger = logging.getLogger("Gateway")

class MCPGateway:
    """
    Translates MCP JSON-RPC requests into standardized ZeroMQ messages natively.
    """
    def __init__(self, broker_req_addr="tcp://127.0.0.1:5557"):
        self.context = zmq.asyncio.Context()
        self.broker_req_addr = broker_req_addr
        self.broker_socket = self.context.socket(zmq.REQ)
        # Timeout settings to prevent deadlocks if the Prime Agent hangs
        self.broker_socket.setsockopt(zmq.RCVTIMEO, 5000) 
        self.broker_socket.connect(self.broker_req_addr)

    async def handle_mcp_request(self, rpc_request: str) -> str:
        """Parses a raw MCP request, encapsulates it, and routes to ZeroMQ Broker."""
        try:
            request = json.loads(rpc_request)
            method = request.get("method")
            params = request.get("params", {})
            req_id = request.get("id", 1)

            # Direct mapping of MCP Tools/Call to the ZeroMQ IPC backend
            if method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                
                ipc_payload = {
                    "target": "prime_agent", 
                    "payload": {
                        "action": "EXECUTE_TOOL",
                        "tool_name": tool_name,
                        "args": args
                    }
                }
                
                # Transmit over IPC
                await self.broker_socket.send_json(ipc_payload)
                
                try:
                    reply = await self.broker_socket.recv_json()
                    response_text = reply.get("data", str(reply))
                except zmq.error.Again:
                    response_text = "[MCP Gateway Error]: Request timed out. Swarm node unresponsive."
                    # Reset REQ socket state after a timeout
                    self.broker_socket.close(linger=0)
                    self.broker_socket = self.context.socket(zmq.REQ)
                    self.broker_socket.setsockopt(zmq.RCVTIMEO, 5000)
                    self.broker_socket.connect(self.broker_req_addr)
                
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": response_text}]
                    }
                })
            else:
                return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}})
                
        except Exception as e:
            logger.error(f"Failed to process MCP request: {e}")
            return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}})
