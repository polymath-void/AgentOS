import zmq
import time
import json
import random

def stream_mock_intents():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5557")
    
    print("Intent Streamer: Connected to ComputeRes Kernel (ROUTER tcp://127.0.0.1:5557)")
    
    intents = [
        {"code": "def run():\n    print('summit')\n    return True", "args": {}},
        {"code": "def run():\n    print('weather')\n    return 'sunny'", "args": {}},
        {"code": "def run():\n    print('claude_ast')\n    return 'ast_wrapped'", "args": {}},
        {"code": "def run():\n    print('hyperbolic_search')\n    return 'vector_found'", "args": {}}
    ]
    
    try:
        while True:
            intent = random.choice(intents)
            print(f"Injecting intent: {intent['code'].split('print')[1][:10]}...")
            
            socket.send_json(intent)
            
            # Non-blocking wait for reply, but we don't strictly care
            # Actually REQ socket MUST wait for a reply before sending again.
            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            if poller.poll(2000): # Wait up to 2 seconds for reply
                socket.recv_json()
            else:
                print("No reply from kernel, resetting socket...")
                socket.close()
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://127.0.0.1:5557")
                
            time.sleep(2.5) # Inject an intent every 2.5 seconds
            
    except KeyboardInterrupt:
        print("Streamer shutting down.")

if __name__ == "__main__":
    stream_mock_intents()
