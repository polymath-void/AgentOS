# Encrypted Swarm Memory Vault

## Overview
A secure, mathematically sharded key-value vault for distributed agent memory retention.

## Features
- **Key Derivation**: Generates secure cryptographic keys using PBKDF2-HMAC (SHA-256).
- **Data Sharding**: Fragments encrypted payloads into distinct chunks.
- **Distributed Storage**: Stores separate shards across independent simulated vault nodes.
- **Reconstruction Protocol**: Safely reassembles and decrypts memory payloads upon request.

## Usage
```bash
python3 main.py
```
