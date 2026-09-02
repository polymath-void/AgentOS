import time
import random
import logging
from dataclasses import dataclass
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='%(message)s')

@dataclass
class DeviceNode:
    name: str
    cpu_usage: float      # 0.0 to 1.0
    ram_usage: float      # 0.0 to 1.0
    battery_level: float  # 0.0 to 1.0
    
    def score(self) -> float:
        # Lower score is better. Weight CPU and Battery heavily.
        # If battery is low (< 20%), penalize heavily.
        battery_penalty = 10.0 if self.battery_level < 0.2 else 0.0
        return (self.cpu_usage * 2) + (self.ram_usage * 1) + ((1.0 - self.battery_level) * 3) + battery_penalty

    def simulate_tick(self):
        # Randomly fluctuate state
        self.cpu_usage = max(0.0, min(1.0, self.cpu_usage + random.uniform(-0.1, 0.1)))
        self.ram_usage = max(0.0, min(1.0, self.ram_usage + random.uniform(-0.05, 0.05)))
        self.battery_level = max(0.0, self.battery_level - random.uniform(0.0, 0.05))

class SwarmOrchestrator:
    def __init__(self):
        self.fleet: List[DeviceNode] = []
        
    def add_node(self, name: str, cpu: float, ram: float, battery: float):
        self.fleet.append(DeviceNode(name, cpu, ram, battery))
        
    def find_best_node(self) -> Optional[DeviceNode]:
        if not self.fleet:
            return None
        # Return node with lowest score
        best_node = min(self.fleet, key=lambda n: n.score())
        return best_node

    def dispatch(self, task_name: str, duration_sec: int):
        best_node = self.find_best_node()
        if best_node:
            logging.info(f"🚀 Dispatching '{task_name}' to {best_node.name} (CPU: {best_node.cpu_usage:.2f}, BAT: {best_node.battery_level:.2f})")
            # Simulate impact
            best_node.cpu_usage = min(1.0, best_node.cpu_usage + 0.3)
        else:
            logging.error("No available nodes in fleet.")

if __name__ == "__main__":
    orchestrator = SwarmOrchestrator()
    orchestrator.add_node("Node-Alpha", cpu=0.2, ram=0.4, battery=0.9)
    orchestrator.add_node("Node-Beta", cpu=0.8, ram=0.7, battery=0.3)
    orchestrator.add_node("Node-Gamma", cpu=0.1, ram=0.2, battery=0.15) # Very low battery

    print("--- Swarm Resource Orchestrator ---")
    tasks = [f"Task-{i}" for i in range(1, 6)]
    
    for task in tasks:
        orchestrator.dispatch(task, 2)
        time.sleep(1)
        # Tick the environment
        for node in orchestrator.fleet:
            node.simulate_tick()
