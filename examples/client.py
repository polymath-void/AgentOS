import argparse
import sys
import os

# Add src to python path securely
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from orchestration.ipc_bus import IPCBus

def main():
    parser = argparse.ArgumentParser(description="ComputeRes Prime Client Terminal")
    parser.add_argument("task", nargs="+", help="The command or task to send to the Prime Agent")
    args = parser.parse_args()
    
    task_string = " ".join(args.task)
    
    ipc = IPCBus()
    ipc.connect()
    
    print(f"[Client] Dispatching task to Prime Agent: '{task_string}'")
    
    # Retry loop to handle ZeroMQ REQ/REP Dealer round-robin load balancing
    for _ in range(5):
        try:
            reply = ipc.request(target="prime_agent", payload={"task": task_string}, timeout=10.0)
            if reply.get("status") == "success":
                print("\n[Antigravity-Prime] Response:")
                print(reply.get("data", {}).get("response", "No response content."))
                return
            elif reply.get("message") == "Target mismatch":
                continue # Bounced off the MCP Daemon; retry for Prime Agent
            else:
                print(f"\n[Error] Prime Agent failed to process: {reply.get('message')}")
                return
        except Exception as e:
            print(f"\n[Fatal] IPC Request failed: {e}")
            return
            
    print("\n[Error] Failed to route to Prime Agent (Max retries exceeded).")

if __name__ == "__main__":
    main()
