import asyncio
import logging
from typing import Dict, Any, Optional, List

from network.mesh import MeshNode
from memory.episodic import EpisodicMemory
from memory.db import SQLiteAdapter
from engine.prompts import PromptMutator
from engine.evolution import SkillSynthesizer
from actors.sandbox import (
    CodeExecutorActor, 
    LogicReasoningActor, 
    NetworkPeerActor, 
    WebScraperActor, 
    OrchestratorActor
)

logger = logging.getLogger("PlaygroundWorkflow")

class PlaygroundWorkflow:
    def __init__(self, node: MeshNode, memory: EpisodicMemory, db: SQLiteAdapter, mutator: Optional[PromptMutator] = None):
        self.node = node
        self.memory = memory
        self.db = db
        self.mutator = mutator or PromptMutator()
        self.synthesizer = SkillSynthesizer()
        self.running = False
        self.loop = None
        
        # Swarm Actors
        self.orchestrator = OrchestratorActor()
        self.code_executor = CodeExecutorActor()
        self.logic_reasoner = LogicReasoningActor()
        self.network_peer = NetworkPeerActor()
        self.web_scraper = WebScraperActor()
        
        self.actors = [
            self.orchestrator,
            self.code_executor,
            self.logic_reasoner,
            self.network_peer,
            self.web_scraper
        ]
        
        # Register active agents with the P2P Mesh Node
        for actor in self.actors:
            self.node.register_agent(actor.name, actor.to_dict())
            
        self.base_instruction = "Analyze task, construct solution, solve accurately."
        
        self._original_handler = self.node.message_handler
        self.node.set_message_handler(self._intercept_message)
        
    def get_actors_status(me) -> List[dict]:
        return [actor.to_dict() for actor in me.actors]

    async def _intercept_message(self, message: dict):
        """Intercepts incoming mesh messages, routes P2P chats, logs State-Action-Obs triplets, and triggers actors."""
        msg_type = message.get("msg_type") or message.get("type", "unknown")
        payload = message.get("payload", {})
        sender = message.get("sender", {})
        
        # 1. Handle Live Inter-Agent P2P Chat Messages
        if msg_type == "AGENT_CHAT":
            sender_name = sender.get("agent", "RemoteAgent")
            recipient_name = message.get("recipient", {}).get("agent", "Broadcast")
            chat_text = payload.get("text", "")
            
            log_content = f"💬 [P2P AGENT CHAT] {sender_name} ➔ {recipient_name}: \"{chat_text}\""
            self.memory.store_event(content=log_content, metadata=message, role=sender_name)
            self.db.insert(role=sender_name, content=log_content, metadata=message)
            logger.info(log_content)
            
        # 2. Handle EvolvOS Self-Evolution Requests
        elif msg_type == "task_evolve":
            skill_name = payload.get("skill_name", "custom_func")
            code_template = payload.get("code", "def custom_func(x): return x * 2")
            assertion = payload.get("assertion", "assert custom_func(5) == 10")
            
            res = await asyncio.to_thread(
                self.synthesizer.synthesize_and_load_skill,
                skill_name, code_template, assertion
            )
            
            status = res.get("status")
            triplet_obs = f"Skill '{skill_name}' synthesis {status}."
            self.memory.log_triplet(
                state=f"Missing capability: {skill_name}",
                action=f"EvolvOS Synthesize & Test Script",
                observation=triplet_obs,
                success=(status == "success"),
                role="EvolvOS Engine"
            )
            
            self.db.insert(role="EvolvOS Engine", content=f"[EVOLVOS SYNTHESIS] {triplet_obs}", metadata=res)
            
        # 3. Handle Code Execution Tasks
        elif msg_type == "task_code_exec":
            code = payload.get("code", "print('Hello Swarm!')")
            output = await asyncio.to_thread(self.code_executor.run_task, code)
            
            self.memory.log_triplet(
                state="Sandboxed Python Task",
                action=f"Exec code: {code[:40]}...",
                observation=output,
                success=not output.startswith("Execution error"),
                role=self.code_executor.name
            )
            
            await self.trigger_event("task_result", {
                "actor": self.code_executor.name,
                "task_type": "code_execution",
                "result": output
            })
            
        # 4. Handle Reasoning Tasks & Prompt Mutations
        elif msg_type == "task_reasoning":
            query = payload.get("query", "Sample reasoning prompt")
            mutated_prompt = self.mutator.mutate_prompt(self.base_instruction)
            
            output = await asyncio.to_thread(self.logic_reasoner.run_task, query, instruction=mutated_prompt)
            
            self.memory.log_triplet(
                state=f"Query: {query}",
                action=f"Evolved Prompt: '{mutated_prompt}'",
                observation=output,
                success=True,
                role=self.logic_reasoner.name
            )
            
            await self.trigger_event("task_result", {
                "actor": self.logic_reasoner.name,
                "task_type": "reasoning",
                "result": output
            })

        # 5. Handle Mesh Relays
        elif msg_type == "task_mesh_broadcast":
            output = await asyncio.to_thread(self.network_peer.run_task, payload)
            await self.trigger_event("task_result", {
                "actor": self.network_peer.name,
                "task_type": "mesh_relay",
                "result": output
            })

        # 6. Handle Task Results
        elif msg_type == "task_result":
            actor = payload.get("actor")
            task_type = payload.get("task_type")
            result = payload.get("result")
            
            self.db.insert(
                role=actor,
                content=f"[{task_type.upper()}] {result}",
                metadata={"task_type": task_type, "payload": payload}
            )

        if self._original_handler:
            if asyncio.iscoroutinefunction(self._original_handler):
                await self._original_handler(message)
            else:
                self._original_handler(message)

    async def trigger_event(self, event_type: str, payload: Dict[str, Any]):
        message = {"type": event_type, "payload": payload}
        await self._intercept_message(message)
        await self.node.broadcast(message)

    async def send_inter_agent_chat(self, sender: str, recipient: str, text: str):
        """Dispatches live P2P inter-agent chat across mesh."""
        packet = await self.node.send_agent_chat(sender, recipient, text)
        await self._intercept_message(packet)

    async def dispatch_user_task(self, task_type: str, data: dict):
        logger.info(f"Swarm Playground task dispatched: {task_type} -> {data}")
        self.orchestrator.state = "active"
        
        if task_type == "chat":
            await self.send_inter_agent_chat(
                data.get("sender", "UserAgent"),
                data.get("recipient", "SwarmPeer"),
                data.get("text", "Hello active agents!")
            )
        elif task_type == "evolve":
            await self.trigger_event("task_evolve", {
                "skill_name": data.get("skill_name", "multiply_power"),
                "code": data.get("code", "def multiply_power(a, b):\n    return (a * b) ** 2"),
                "assertion": data.get("assertion", "assert multiply_power(2, 3) == 36")
            })
        elif task_type == "code":
            await self.trigger_event("task_code_exec", {"code": data.get("code", "print('Swarm Code Execution Test')")})
        elif task_type == "reasoning":
            await self.trigger_event("task_reasoning", {"query": data.get("query", "Explain Quantum Mechanics")})
        elif task_type == "mesh":
            await self.trigger_event("task_mesh_broadcast", {"msg": data.get("msg", "P2P Network Broadcast Test")})
            
        self.orchestrator.state = "idle"

    async def run(self, seed_tasks=None):
        self.running = True
        self.loop = asyncio.get_running_loop()
        logger.info("Autonomous Swarm Workflow active.")
        
        # 1. Live Inter-Agent Chat Demo
        await self.send_inter_agent_chat("Agent-Termux", "Agent-Desktop", "Greetings peer node! Initiating collaborative swarm session.")
        await asyncio.sleep(2)
        
        # 2. EvolvOS Self-Evolution Skill Synthesis Demo
        await self.dispatch_user_task("evolve", {
            "skill_name": "compute_fibonacci",
            "code": "def compute_fibonacci(n):\n    if n <= 1: return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
            "assertion": "assert compute_fibonacci(10) == 55"
        })
        await asyncio.sleep(2)
        
        # 3. Sandboxed Code Execution
        await self.dispatch_user_task("code", {"code": "import sys; print(f'Swarm Subprocess Engine: Python {sys.version.split()[0]}')"})

    def stop(self):
        self.running = False
