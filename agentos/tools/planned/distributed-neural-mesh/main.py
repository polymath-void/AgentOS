import os
import json
import base64
import hashlib
import time
import threading
import queue
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s')

def simple_encrypt(data: str, key: str) -> str:
    # Extremely basic XOR + Base64 for simulated encryption
    encoded = bytearray(data, 'utf-8')
    key_bytes = bytearray(key, 'utf-8')
    for i in range(len(encoded)):
        encoded[i] ^= key_bytes[i % len(key_bytes)]
    return base64.b64encode(encoded).decode('utf-8')

def simple_decrypt(enc_data: str, key: str) -> str:
    encoded = bytearray(base64.b64decode(enc_data))
    key_bytes = bytearray(key, 'utf-8')
    for i in range(len(encoded)):
        encoded[i] ^= key_bytes[i % len(key_bytes)]
    return encoded.decode('utf-8')

class MeshNode(threading.Thread):
    def __init__(self, node_id: int, task_queue: queue.Queue, result_queue: queue.Queue, shared_key: str):
        super().__init__(name=f"Node-{node_id}")
        self.node_id = node_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.shared_key = shared_key
        self.daemon = True

    def run(self):
        logging.info("Node online and waiting for encrypted payloads.")
        while True:
            try:
                task = self.task_queue.get(timeout=2)
                if task is None:
                    break # Shutdown signal
                
                enc_payload = task['payload']
                logging.info(f"Received encrypted chunk: {enc_payload[:10]}...")
                
                # Decrypt
                decrypted = simple_decrypt(enc_payload, self.shared_key)
                # Process (e.g., reverse string or compute)
                processed = decrypted.upper() + " [PROCESSED]"
                time.sleep(0.5) # Simulate work
                
                # Encrypt response
                enc_response = simple_encrypt(processed, self.shared_key)
                self.result_queue.put({"node_id": self.node_id, "chunk_id": task['chunk_id'], "result": enc_response})
                self.task_queue.task_done()
                
            except queue.Empty:
                continue

class NeuralMeshOrchestrator:
    def __init__(self, num_nodes: int):
        self.num_nodes = num_nodes
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.shared_key = "SuperSecretMeshKey2026"
        self.nodes = []

    def start_mesh(self):
        for i in range(self.num_nodes):
            node = MeshNode(i, self.task_queue, self.result_queue, self.shared_key)
            node.start()
            self.nodes.append(node)

    def dispatch_task(self, data_chunks: List[str]):
        logging.info(f"Orchestrator: Encrypting and dispatching {len(data_chunks)} chunks to Mesh...")
        for i, chunk in enumerate(data_chunks):
            enc_chunk = simple_encrypt(chunk, self.shared_key)
            self.task_queue.put({"chunk_id": i, "payload": enc_chunk})

    def collect_results(self, expected_count: int):
        results = []
        while len(results) < expected_count:
            res = self.result_queue.get()
            dec_result = simple_decrypt(res['result'], self.shared_key)
            logging.info(f"Orchestrator: Node-{res['node_id']} completed chunk {res['chunk_id']} -> {dec_result}")
            results.append((res['chunk_id'], dec_result))
        
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]

    def shutdown(self):
        for _ in self.nodes:
            self.task_queue.put(None)
        for node in self.nodes:
            node.join()
        logging.info("Mesh network gracefully shut down.")

if __name__ == "__main__":
    mesh = NeuralMeshOrchestrator(num_nodes=3)
    mesh.start_mesh()
    
    # Test Data
    data = ["compute_alpha", "compute_beta", "compute_gamma", "compute_delta", "compute_epsilon"]
    mesh.dispatch_task(data)
    
    final_output = mesh.collect_results(len(data))
    logging.info(f"Final Assembled Result: {final_output}")
    mesh.shutdown()
