import ast
import uuid
import time
from typing import Dict, Any, List

class CRDTNode:
    """
    A mathematical wrapper around an AST node that applies Conflict-Free Replicated Data Type (CRDT)
    Last-Write-Wins (LWW) properties.
    """
    def __init__(self, node_id: str, ast_node: ast.AST, timestamp: float):
        self.node_id = node_id
        self.ast_node = ast_node
        self.timestamp = timestamp
        self.tombstone = False

    def update(self, new_ast_node: ast.AST, new_timestamp: float):
        if new_timestamp > self.timestamp:
            self.ast_node = new_ast_node
            self.timestamp = new_timestamp
            self.tombstone = False

    def delete(self, new_timestamp: float):
        if new_timestamp > self.timestamp:
            self.tombstone = True
            self.timestamp = new_timestamp

class ASTManager:
    """
    Manages the parsing, CRDT mutation, and unparsing of a Python codebase.
    Prevents syntax breakage by ensuring all edits are valid AST mutations.
    """
    def __init__(self, source_code: str):
        self.tree = ast.parse(source_code)
        self.crdt_registry: Dict[str, CRDTNode] = {}
        self._index_tree()

    def _index_tree(self):
        """Recursively index the AST into CRDT wrappers."""
        for node in ast.walk(self.tree):
            # We assign deterministic IDs to functions and classes for merging across the network
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                node_id = f"def_{node.name}"
                self.crdt_registry[node_id] = CRDTNode(node_id, node, time.time())

    def inject_function(self, function_code: str) -> str:
        """
        Safely injects or updates a function natively via AST without merge conflicts.
        """
        new_module = ast.parse(function_code)
        for node in new_module.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                node_id = f"def_{node.name}"
                timestamp = time.time()
                
                if node_id in self.crdt_registry:
                    # Update existing CRDT node (Last-Write-Wins)
                    self.crdt_registry[node_id].update(node, timestamp)
                else:
                    # Inject new CRDT node
                    self.crdt_registry[node_id] = CRDTNode(node_id, node, timestamp)
                    self.tree.body.append(node)
                
                return f"Successfully injected {node_id} into the CRDT AST Layer."
                
        return "Failed to find valid function in injection payload."

    def compile_to_source(self) -> str:
        """
        Reconstructs the pure python string from the underlying CRDT-managed AST.
        Automatically strips out tombstoned nodes.
        """
        # Rebuild the body based on active CRDT nodes
        active_body = []
        for node in self.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                node_id = f"def_{node.name}"
                crdt = self.crdt_registry.get(node_id)
                if crdt and not crdt.tombstone:
                    active_body.append(crdt.ast_node)
            else:
                active_body.append(node)
                
        self.tree.body = active_body
        return ast.unparse(self.tree)

if __name__ == "__main__":
    # Internal Unit Test
    initial_code = '''
def hello():
    print("Hello Swarm")
'''
    manager = ASTManager(initial_code)
    
    # Simulate Agent 1 injecting a new function
    agent_1_mutation = '''
def calculate_fuel():
    return 100
'''
    manager.inject_function(agent_1_mutation)
    
    # Simulate Agent 2 updating the existing function (Conflict Resolution)
    agent_2_mutation = '''
def hello():
    print("Hello Decentralized Swarm!")
'''
    manager.inject_function(agent_2_mutation)
    
    print("--- Final Source Code via CRDT ---")
    print(manager.compile_to_source())
