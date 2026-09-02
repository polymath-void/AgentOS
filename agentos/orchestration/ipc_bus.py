import zmq
import json
import threading
import logging
from typing import Callable, Any, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("IPCBus")

class IPCBus:
    """
    ZeroMQ-based Inter-Process Communication Bus for AgentOS.
    Supports Publish/Subscribe for events and Request/Reply for direct communication.
    """
    def __init__(self, pub_addr="tcp://127.0.0.1:5555", sub_addr="tcp://127.0.0.1:5556", req_addr="tcp://127.0.0.1:5557", rep_addr="tcp://127.0.0.1:5558"):
        self.context = zmq.Context()
        
        self.pub_addr = pub_addr
        self.sub_addr = sub_addr
        self.req_addr = req_addr
        self.rep_addr = rep_addr
        
        self.pub_socket = self.context.socket(zmq.PUB)
        self.req_socket = self.context.socket(zmq.REQ)
        
    def connect(self):
        """Connects to the central IPC Broker."""
        self.pub_socket.connect(self.pub_addr)
        self.req_socket.connect(self.req_addr)
        logger.info(f"IPCBus connected to {self.pub_addr} and {self.req_addr}")

    def publish(self, topic: str, message: Dict[str, Any]):
        """Publish an event to a topic."""
        payload = json.dumps(message)
        self.pub_socket.send_multipart([topic.encode('utf-8'), payload.encode('utf-8')])
        logger.debug(f"Published to {topic}: {payload}")

    def subscribe(self, topic: str, callback: Callable[[str, Dict[str, Any]], None]):
        """Subscribe to a topic in a background thread."""
        def sub_worker():
            sub_socket = self.context.socket(zmq.SUB)
            sub_socket.connect(self.sub_addr)
            sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            logger.info(f"Subscribed to topic: {topic}")
            while True:
                try:
                    topic_bytes, payload_bytes = sub_socket.recv_multipart()
                    msg_topic = topic_bytes.decode('utf-8')
                    msg_payload = json.loads(payload_bytes.decode('utf-8'))
                    callback(msg_topic, msg_payload)
                except Exception as e:
                    logger.error(f"Error in subscribe worker: {e}")

        thread = threading.Thread(target=sub_worker, daemon=True)
        thread.start()

    def request(self, target: str, payload: Dict[str, Any], timeout=5.0) -> Dict[str, Any]:
        """Send a request to a target and wait for a reply."""
        message = {
            "target": target,
            "payload": payload
        }
        self.req_socket.send_json(message)
        
        poller = zmq.Poller()
        poller.register(self.req_socket, zmq.POLLIN)
        if poller.poll(timeout * 1000):
            reply = self.req_socket.recv_json()
            return reply
        else:
            self.req_socket.setsockopt(zmq.LINGER, 0)
            self.req_socket.close()
            self.req_socket = self.context.socket(zmq.REQ)
            self.req_socket.connect(self.req_addr)
            raise TimeoutError(f"Request to {target} timed out after {timeout} seconds.")

    def start_reply_server(self, target: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Start a reply server listening for requests to a specific target."""
        def rep_worker():
            rep_socket = self.context.socket(zmq.REP)
            rep_socket.connect(self.rep_addr)
            logger.info(f"Reply server started for target: {target}")
            
            while True:
                try:
                    request = rep_socket.recv_json()
                    if request.get("target") == target:
                        response = handler(request.get("payload", {}))
                        rep_socket.send_json({"status": "success", "data": response})
                    else:
                        rep_socket.send_json({"status": "error", "message": "Target mismatch"})
                except Exception as e:
                    logger.error(f"Error in reply server: {e}")
                    rep_socket.send_json({"status": "error", "message": str(e)})

        thread = threading.Thread(target=rep_worker, daemon=True)
        thread.start()

class IPCBroker:
    """Central Message Broker for routing Pub/Sub and Req/Rep."""
    def __init__(self, xpub_addr="tcp://*:5555", xsub_addr="tcp://*:5556", router_addr="tcp://*:5557", dealer_addr="tcp://*:5558"):
        self.context = zmq.Context()
        self.xpub_addr = xpub_addr
        self.xsub_addr = xsub_addr
        self.router_addr = router_addr
        self.dealer_addr = dealer_addr

    def start(self):
        """Starts the broker blocking the current thread."""
        logger.info("Starting IPC Broker...")
        
        def pubsub_proxy():
            xpub = self.context.socket(zmq.XPUB)
            xpub.bind(self.xsub_addr)
            xsub = self.context.socket(zmq.XSUB)
            xsub.bind(self.xpub_addr)
            zmq.proxy(xpub, xsub)

        def reqrep_proxy():
            router = self.context.socket(zmq.ROUTER)
            router.bind(self.router_addr)
            dealer = self.context.socket(zmq.DEALER)
            dealer.bind(self.dealer_addr)
            zmq.proxy(router, dealer)

        t1 = threading.Thread(target=pubsub_proxy, daemon=True)
        t2 = threading.Thread(target=reqrep_proxy, daemon=True)
        t1.start()
        t2.start()
        logger.info("IPC Broker running.")
        t1.join()
        t2.join()
