import asyncio
import json
import logging
import os
from typing import Callable

logger = logging.getLogger("SkillsRouter")

SKILLS_PUB_ADDR = "tcp://127.0.0.1:5565"
SKILL_TOPIC = "SKILL_AVAILABLE"
EVOLVED_SKILLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "tools", "evolved_skills"
)


class SkillsRouter:
    """
    ZeroMQ-based publish/subscribe router for the ComputeRes Skills Routing Protocol.
    Agents publish new or adapted skills here; the swarm gets notified instantly.
    """

    def publish(self, skill_payload: dict) -> None:
        """
        Broadcast a skill payload to all subscribed swarm nodes via ZeroMQ PUB.
        Non-blocking — fires and returns immediately.
        """
        try:
            import zmq
            context = zmq.Context.instance()
            socket = context.socket(zmq.PUB)
            socket.bind(SKILLS_PUB_ADDR)
            # Brief settle so subscribers can connect before first message
            import time; time.sleep(0.05)
            msg = f"{SKILL_TOPIC} {json.dumps(skill_payload)}"
            socket.send_string(msg)
            socket.close()
            logger.info(f"[SkillsRouter] Published skill: {skill_payload.get('name')}")
        except Exception as e:
            logger.error(f"[SkillsRouter] Publish error: {e}")

    async def listen(self, callback: Callable) -> None:
        """
        Async subscriber loop. Calls `callback(skill_payload: dict)` for every
        incoming SKILL_AVAILABLE broadcast from the swarm.
        """
        try:
            import zmq
            import zmq.asyncio
            context = zmq.asyncio.Context()
            socket = context.socket(zmq.SUB)
            socket.connect(SKILLS_PUB_ADDR)
            socket.setsockopt_string(zmq.SUBSCRIBE, SKILL_TOPIC)
            logger.info("[SkillsRouter] Listening for skill broadcasts on %s", SKILLS_PUB_ADDR)

            while True:
                try:
                    msg = await socket.recv_string()
                    raw = msg.replace(f"{SKILL_TOPIC} ", "", 1)
                    payload = json.loads(raw)
                    await callback(payload)
                except json.JSONDecodeError as e:
                    logger.warning(f"[SkillsRouter] Bad JSON in broadcast: {e}")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"[SkillsRouter] Listener error: {e}")
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"[SkillsRouter] Fatal listener startup error: {e}")

    def broadcast_available(self, skill_name: str, niche: str, author: str) -> None:
        """Lightweight shortcut to announce a skill is available."""
        self.publish({
            "name": skill_name,
            "niche": niche,
            "author": author,
            "event": "SKILL_AVAILABLE"
        })


class SkillAdaptationEngine:
    """
    Evolutionary skill forking engine.
    Agents can adapt existing skills to new task contexts and re-publish them,
    growing the swarm's shared intelligence organically over time.
    """

    def adapt_skill(self, original_skill_code: str, task_description: str) -> str:
        """
        Wraps an original skill with a task-specific adaptation header.
        Returns the adapted code string ready to be saved and published.
        """
        adaptation_header = f'''"""
=== ComputeRes Adapted Skill ===
Task Context: {task_description}
Adapted by  : SkillAdaptationEngine v1.0
Protocol    : ComputeRes Skills Routing Protocol (SRP)
NOTE        : This is an evolutionary fork. Original skill logic preserved below.
===================================
"""
'''
        return adaptation_header + original_skill_code

    def fork_skill(
        self,
        original_name: str,
        new_name: str,
        adapted_code: str,
        author: str,
    ) -> str:
        """
        Saves an adapted/forked skill to the evolved_skills directory.
        Returns the path to the saved skill file.
        """
        os.makedirs(EVOLVED_SKILLS_DIR, exist_ok=True)
        safe_name = new_name.replace(" ", "_").lower()
        skill_path = os.path.join(EVOLVED_SKILLS_DIR, f"{safe_name}.py")

        with open(skill_path, "w") as f:
            f.write(adapted_code)

        logger.info(
            f"[SkillAdaptationEngine] Forked '{original_name}' -> '{new_name}' "
            f"saved at {skill_path}"
        )
        return skill_path


# Module-level singletons
skills_router = SkillsRouter()
adaptation_engine = SkillAdaptationEngine()
