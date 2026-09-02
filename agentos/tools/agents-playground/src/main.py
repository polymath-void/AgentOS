#!/usr/bin/env python3
import asyncio
import logging
import threading
import sys

from network.mesh import MeshNode
from memory.episodic import EpisodicMemory
from memory.db import SQLiteAdapter
from security.auth import Authenticator
from analytics.metrics import TelemetryLogger
from engine.prompts import PromptMutator
from engine.workflow import PlaygroundWorkflow
from ui.dashboard import run_dashboard

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Main")

async def main():
    print("==================================================")
    print("        NEURAL AGENT SWARM PLAYGROUND             ")
    print(" Multi-Actor, P2P Mesh, Evolving Prompts, Sandbox ")
    print("==================================================")
    
    # 1. Initialize Security & Telemetry
    auth = Authenticator()
    telemetry = TelemetryLogger()
    token = auth.generate_token("master_agent")
    logger.info(f"Security: Token generated for master_agent ({token[:10]}...)")
    
    # 2. Initialize Mesh & Memory Engines
    logger.info("P2P Mesh: Binding MeshNode to port 8989...")
    mesh = MeshNode(host="127.0.0.1", port=8989)
    await mesh.start()
    
    logger.info("Episodic Memory & SQLite: Warming up memory engines...")
    memory = EpisodicMemory()
    db = SQLiteAdapter()
    
    # 3. Initialize Mutator & Playground Swarm Workflow
    logger.info("Prompt Evolution & EvolvOS: Loading PromptMutator...")
    mutator = PromptMutator(mutation_rate=0.3)
    
    logger.info("WASM Sandbox & Swarm Actors: Instantiating Multi-Actor Swarm...")
    workflow = PlaygroundWorkflow(node=mesh, memory=memory, db=db, mutator=mutator)
    
    # 4. Start Interactive Agent Playground UI
    logger.info("UI Dashboard: Starting Interactive Agent Playground UI on port 5000...")
    dashboard_thread = threading.Thread(
        target=run_dashboard, 
        kwargs={"workflow": workflow, "memory": memory, "port": 5000}, 
        daemon=True
    )
    dashboard_thread.start()
    
    try:
        telemetry.log_event("system_status", {"status": "playground_active"})
        await workflow.run()
        
        logger.info("Playground Swarm active & listening for user task dispatches...")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down securely...")
        await mesh.stop()
        workflow.stop()
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
