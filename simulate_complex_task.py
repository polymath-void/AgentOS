import zmq
import time
import json
import random
import sys

def main():
    print("Starting ComputeRes Swarm Simulator...")
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5562")
    
    # Allow time for SUBs to connect
    time.sleep(1.0)
    print("Bound to tcp://127.0.0.1:5562. Publishing swarm telemetry...")

    scenarios = [
        {"agent": "Claude", "code": "summit global scaling logic init"},
        {"agent": "Copilot", "code": "web server routing established on port 8080"},
        {"agent": "Gemini", "code": "hyperbolic_vector_search(query='AST mutation')"},
        {"agent": "Cursor", "code": "crdt_ast_mutate(file='mesh.py')"},
        {"agent": "SwarmWorker", "code": "allocate_wasm_fuel(15000)"},
        {"agent": "SecurityGuard", "code": "validate_capability(network=True)"},
        {"agent": "MemEngine", "code": "indexing new episodic chunk..."},
        {"agent": "Claude", "code": "analyzing ZeroMQ IPC bottleneck"},
    ]

    try:
        iteration = 0
        while True:
            scenario = random.choice(scenarios)
            # Add some dynamic variety
            payload = {
                "agent": scenario["agent"],
                "code": scenario["code"] + f" [ID: {random.randint(1000, 9999)}]",
                "timestamp": time.time(),
                "iteration": iteration
            }
            
            message = f"TELEMETRY {json.dumps(payload)}"
            socket.send_string(message)
            print(f"Sent: {message}")
            
            # Complex burst simulation
            if random.random() > 0.8:
                time.sleep(0.1) # Burst of activity
            else:
                time.sleep(random.uniform(0.5, 2.5))
            iteration += 1
            
            # Every 10 iterations, simulate a "summit" event
            if iteration % 10 == 0:
                summit_payload = {
                    "agent": "System",
                    "code": "summit triggered: reorganizing swarm roles"
                }
                socket.send_string(f"TELEMETRY {json.dumps(summit_payload)}")
                print(f"Sent Summit Event: {summit_payload}")
                time.sleep(2.0)

    except KeyboardInterrupt:
        print("Simulation stopped by user.")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
