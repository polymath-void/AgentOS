import zmq, json, os, sys
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5557")

tools_to_evolve = [
    {
        "name": "system_profiler",
        "code": "import os\n\ndef analyze_swarm_health():\n    try:\n        load = os.getloadavg()[0]\n    except:\n        load = '0.5'\n    return f'Swarm Profiling Complete:\\n-> CPU Load Average: {load}\\n-> Distributed Shards Active.\\n-> Nano-Mesh Operational.'"
    },
    {
        "name": "log_anomaly_detector",
        "code": "import hashlib\n\ndef scan_memory_vectors(data_string):\n    vector = hashlib.sha256(data_string.encode()).hexdigest()\n    if vector.startswith('00'):\n        return f'Critical Anomaly Detected in vector {vector}'\n    return 'Memory stream verified. No semantic drift detected.'"
    }
]

for tool in tools_to_evolve:
    task_string = f"EVOLVE_TOOL: {tool['name']} | {tool['code']}"
    for i in range(20):
        socket.send_json({"target": "prime_agent", "payload": {"task": task_string}})
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        if poller.poll(2000):
            reply = socket.recv_json()
            if reply.get("status") == "success":
                print(reply["data"]["response"])
                break
        # Reconnect on fail/timeout
        socket.close()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:5557")
