import zmq
import zmq.asyncio
import asyncio
import logging
import os

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] IPCBroker: %(message)s')
logger = logging.getLogger("Broker")

class IPCBroker:
    """
    The High-Throughput Local Nervous System.
    Uses Asyncio ZeroMQ to route JSON-RPC/MCP intents from the Gateway to local WASM edge workers.
    """
    def __init__(self, router_bind_addr="tcp://127.0.0.1:5557", dealer_bind_addr="tcp://127.0.0.1:5558"):
        self.context = zmq.asyncio.Context()
        self.router_bind_addr = router_bind_addr
        self.dealer_bind_addr = dealer_bind_addr
        
        self.router = self.context.socket(zmq.ROUTER)
        self.dealer = self.context.socket(zmq.DEALER)
        
        # Optimize High-Water Marks to prevent memory leaks during massive swarm events
        self.router.setsockopt(zmq.RCVHWM, 10000)
        self.dealer.setsockopt(zmq.SNDHWM, 10000)
        
        self.router.bind(self.router_bind_addr)
        self.dealer.bind(self.dealer_bind_addr)
        
        self.is_running = False

    async def start(self):
        """Asynchronously proxies messages between Gateway and Workers without blocking."""
        logger.info(f"Initialized ROUTER at {self.router_bind_addr} | DEALER at {self.dealer_bind_addr}")
        self.is_running = True
        
        try:
            # Native ZeroMQ proxy logic written manually for pure asyncio compatibility
            poller = zmq.asyncio.Poller()
            poller.register(self.router, zmq.POLLIN)
            poller.register(self.dealer, zmq.POLLIN)
            
            while self.is_running:
                events = await poller.poll(1000)
                events_dict = dict(events)
                
                if self.router in events_dict:
                    message = await self.router.recv_multipart()
                    await self.dealer.send_multipart(message)
                    
                if self.dealer in events_dict:
                    message = await self.dealer.recv_multipart()
                    await self.router.send_multipart(message)
                    
        except asyncio.CancelledError:
            logger.info("Broker proxy task cleanly cancelled.")
        except Exception as e:
            logger.error(f"Fatal anomaly in Broker Proxy routing: {e}")
        finally:
            self.stop()
            
    def stop(self):
        self.is_running = False
        self.router.close(linger=0)
        self.dealer.close(linger=0)
        self.context.term()
        logger.info("IPC Broker gracefully terminated and sockets released.")
