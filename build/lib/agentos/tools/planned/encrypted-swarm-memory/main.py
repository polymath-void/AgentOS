import hashlib
import json
import os
import base64
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class VaultNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.storage = {}

    def store_shard(self, key: str, shard: str):
        self.storage[key] = shard
        
    def retrieve_shard(self, key: str) -> str:
        return self.storage.get(key, "")

class EncryptedSwarmMemory:
    def __init__(self):
        self.nodes = [VaultNode("Node-1"), VaultNode("Node-2"), VaultNode("Node-3")]
        self.master_key = b"SwarmMasterKey_2026"
        
    def _derive_key(self, key_name: str) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', self.master_key, key_name.encode(), 100000)

    def _xor_encrypt(self, text: str, key: bytes) -> str:
        text_bytes = text.encode()
        encrypted = bytearray()
        for i in range(len(text_bytes)):
            encrypted.append(text_bytes[i] ^ key[i % len(key)])
        return base64.b64encode(encrypted).decode()

    def _xor_decrypt(self, enc_b64: str, key: bytes) -> str:
        enc_bytes = base64.b64decode(enc_b64)
        decrypted = bytearray()
        for i in range(len(enc_bytes)):
            decrypted.append(enc_bytes[i] ^ key[i % len(key)])
        return decrypted.decode()

    def store_memory(self, memory_id: str, payload: dict):
        logging.info(f"🔒 Encrypting and sharding memory: '{memory_id}'")
        raw_data = json.dumps(payload)
        key = self._derive_key(memory_id)
        enc_data = self._xor_encrypt(raw_data, key)
        
        # Simple sharding: split into N chunks
        chunk_size = max(1, len(enc_data) // len(self.nodes) + 1)
        shards = [enc_data[i:i+chunk_size] for i in range(0, len(enc_data), chunk_size)]
        
        for idx, node in enumerate(self.nodes):
            shard_data = shards[idx] if idx < len(shards) else ""
            node.store_shard(memory_id, shard_data)
            logging.info(f"   -> Shard {idx+1} safely locked in {node.node_id}")

    def retrieve_memory(self, memory_id: str) -> dict:
        logging.info(f"🔓 Retrieving and reassembling memory: '{memory_id}'")
        key = self._derive_key(memory_id)
        
        reassembled = ""
        for node in self.nodes:
            reassembled += node.retrieve_shard(memory_id)
            
        try:
            decrypted = self._xor_decrypt(reassembled, key)
            return json.loads(decrypted)
        except Exception as e:
            logging.error("Failed to decrypt or reconstruct memory!")
            return {}

if __name__ == "__main__":
    swarm_memory = EncryptedSwarmMemory()
    
    # Store critical data
    secret_payload = {
        "agent_objective": "Infiltrate target OS",
        "last_known_hash": "a8f5f167f44f4964e6c998dee827110c",
        "status": "active"
    }
    
    swarm_memory.store_memory("objective_alpha", secret_payload)
    
    print("\n--- Simulating Memory Retrieval ---")
    retrieved = swarm_memory.retrieve_memory("objective_alpha")
    
    print(json.dumps(retrieved, indent=2))
