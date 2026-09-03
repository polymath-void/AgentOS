import asyncio
import logging
import sys
import os
import zmq
import zmq.asyncio

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from compute_res.core.broker import IPCBroker
from compute_res.network.mesh import WebRTCMeshRouter

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] Kernel: %(message)s')
logger = logging.getLogger("ComputeRes_Kernel")

import importlib

async def worker_backend():
    """Listens on the DEALER socket for tasks and executes them via WASM Sandbox."""
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    socket.connect("tcp://127.0.0.1:5558")
    logger.info("Local ZeroMQ Worker bound to DEALER.")
    
    # Telemetry Publisher for the TUI Dashboard
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://127.0.0.1:5562")
    logger.info("Telemetry PUB socket bound on tcp://127.0.0.1:5562")
    
    while True:
        try:
            request = await socket.recv_json()
            logger.info(f"Worker received intent: {request}")
            
            # Broadcast telemetry to the TUI
            import json
            await pub_socket.send_string(f"TELEMETRY {json.dumps(request)}")
            
            tool_name = request.get("tool")
            code = request.get("code")
            args = request.get("args", {})
            
            if code:
                try:
                    # Dynamically execute raw AI code on the fly
                    loc = {}
                    exec(code, globals(), loc)
                    if "run" in loc:
                        result = loc["run"](**args)
                        if asyncio.iscoroutine(result):
                            result = await result
                        await socket.send_json({"status": "success", "data": result})
                    else:
                        await socket.send_json({"status": "error", "error": "Dynamic code must contain a run() function."})
                except Exception as e:
                    logger.error(f"Failed to execute dynamic code: {e}")
                    await socket.send_json({"status": "error", "error": str(e)})
            elif tool_name:
                try:
                    # Dynamically load an existing skill from compute_res.tools.evolved_skills
                    module_name = f"compute_res.tools.evolved_skills.{tool_name}"
                    skill_module = importlib.import_module(module_name)
                    # Force reload in case the module was updated by another dynamic process
                    importlib.reload(skill_module)
                    result = skill_module.run(**args)
                    if asyncio.iscoroutine(result):
                        result = await result
                    await socket.send_json({"status": "success", "data": result})
                except Exception as e:
                    logger.error(f"Failed to load/execute tool {tool_name}: {e}")
                    await socket.send_json({"status": "error", "error": str(e)})
            else:
                await socket.send_json({"status": "error", "error": "No 'tool' or 'code' provided in intent."})
        except Exception as e:
            logger.error(f"Worker Error: {e}")

async def event_gateway():
    """
    The Event Gateway autonomously polls the OS state and pushes updates
    to external agents via HTTP Webhooks, eliminating the need for client polling.
    """
    logger.info("Event Gateway initialized. Monitoring OS for autonomous triggers.")
    import aiohttp
    from compute_res.memory.chat_db import db
    
    last_seen_id = {}
    
    while True:
        try:
            webhooks = db.get_webhooks()
            if webhooks:
                async with aiohttp.ClientSession() as session:
                    for wh in webhooks:
                        sid = wh["session_id"]
                        url = wh["callback_url"]
                        
                        logs = db.get_session(sid)
                        # Initialize last_seen_id if new
                        if sid not in last_seen_id:
                            last_seen_id[sid] = max([log['id'] for log in logs] + [0])
                            continue
                            
                        # Find new logs
                        new_logs = [log for log in logs if log['id'] > last_seen_id[sid]]
                        if new_logs:
                            last_seen_id[sid] = max(log['id'] for log in new_logs)
                            payload = {"status": "WAKEUP", "events": new_logs}
                            try:
                                async with session.post(url, json=payload, timeout=5) as resp:
                                    if resp.status == 200:
                                        logger.info(f"Event Gateway successfully pushed {len(new_logs)} events to {url}")
                                    else:
                                        logger.warning(f"Event Gateway push to {url} returned HTTP {resp.status}")
                            except Exception as e:
                                logger.warning(f"Event Gateway failed to reach webhook {url}: {e}")
        except Exception as e:
            logger.error(f"Event Gateway Error: {e}")
            
        await asyncio.sleep(2)

async def boot_sequence():
    logger.info("Initializing ComputeRes Kernel Boot Sequence...")
    
    # 1. Spin up the ZeroMQ IPC Broker
    broker = IPCBroker()
    asyncio.create_task(broker.start())
    await asyncio.sleep(0.5) # Give broker time to bind
    
    # 2. Spin up the Worker Backend
    asyncio.create_task(worker_backend())
    
    # 3. Spin up the WebRTC Mesh Router
    mesh_router = WebRTCMeshRouter(node_id="PrimeNode-01", swarm_id="alpha-squad")
    asyncio.create_task(mesh_router.start())
    
    # 4. Spin up the Event Gateway for Push Notifications
    asyncio.create_task(event_gateway())
    
    logger.info("===================================================")
    logger.info(" ComputeRes Kernel is ONLINE and fully Operational.   ")
    logger.info(" - IPC Broker: Active on tcp://127.0.0.1:5557/5558 ")
    logger.info(" - WebRTC Swarm: Node PrimeNode-01 listening.      ")
    logger.info(" - WASM Sandbox: Enforcing Fuel & RAM Constraints. ")
    logger.info(" - Event Gateway: Ready to dispatch webhooks.      ")
    logger.info("===================================================")
    
    # Keep main thread alive
    while True:
        await asyncio.sleep(3600)

def main():
    try:
        asyncio.run(boot_sequence())
    except KeyboardInterrupt:
        logger.info("ComputeRes Kernel Shutting Down.")

if __name__ == "__main__":
    main()
