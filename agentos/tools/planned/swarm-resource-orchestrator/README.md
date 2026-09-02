# Swarm Resource Orchestrator

## Overview
An intelligent load balancer designed to optimize task routing across a fleet of active devices.

## Features
- **Dynamic Node Scoring**: Calculates fitness scores based on CPU usage, RAM, and Battery life.
- **Battery Penalty Matrix**: Implements severe penalties for nodes dropping below 20% battery.
- **Live State Fluctuations**: Simulates real-time hardware state changes during runtime.
- **Optimal Dispatch**: Routes incoming swarm directives to the most capable node in the fleet.

## Usage
```bash
python3 main.py
```
