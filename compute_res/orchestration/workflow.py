from .agent import BaseAgent

class WorkflowDAG:
    def __init__(self):
        self.nodes = {}

    def add_node(self, step_name: str, agent: BaseAgent):
        self.nodes[step_name] = agent

    def execute_pipeline(self):
        for step, agent in self.nodes.items():
            print(f"Executing step {step} with {agent.name}")
