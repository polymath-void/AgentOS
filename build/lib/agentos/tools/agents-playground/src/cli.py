#!/usr/bin/env python3
import sys
import argparse
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def dispatch_task(task_type, payload_data):
    print(f"[*] Dispatching '{task_type}' task to Autonomous Swarm Playground...")
    body = {"type": task_type, **payload_data}
    try:
        res = requests.post(f"{BASE_URL}/api/dispatch", json=body)
        print("[+] Swarm Response:", res.json())
    except Exception as e:
        print("[-] Error connecting to Agent Playground server:", e)

def search_memory(query):
    print(f"[*] Searching Episodic Memory Graph for: '{query}'")
    try:
        res = requests.get(f"{BASE_URL}/api/search?q={query}")
        results = res.json()
        print(f"\nFound {len(results)} memory records:\n" + "="*50)
        for r in results:
            role = r.get("role", r[2] if isinstance(r, list) and len(r)>2 else "Swarm Event")
            content = r.get("content", r[3] if isinstance(r, list) and len(r)>3 else "")
            print(f"[{role}] {content}\n" + "-"*50)
    except Exception as e:
        print("[-] Error querying Playground memory:", e)

def main():
    parser = argparse.ArgumentParser(description="Autonomous Neural Swarm Playground CLI Client")
    subparsers = parser.add_subparsers(dest="command")

    chat_p = subparsers.add_parser("chat", help="Send live P2P chat message between agents")
    chat_p.add_argument("--sender", default="Agent-Alpha", help="Sender agent name")
    chat_p.add_argument("--recipient", default="Agent-Beta", help="Recipient agent name")
    chat_p.add_argument("--text", required=True, help="Message text")

    evolve_p = subparsers.add_parser("evolve", help="Trigger EvolvOS self-evolving skill synthesis")
    evolve_p.add_argument("--name", required=True, help="Skill function name")
    evolve_p.add_argument("--code", required=True, help="Python function implementation code")
    evolve_p.add_argument("--assertion", required=True, help="Test assertion code")

    code_p = subparsers.add_parser("code", help="Dispatch Python snippet for sandboxed execution")
    code_p.add_argument("--snippet", required=True, help="Python code to execute")

    reason_p = subparsers.add_parser("reason", help="Dispatch logic reasoning task with prompt evolution")
    reason_p.add_argument("--query", required=True, help="Prompt query")

    mesh_p = subparsers.add_parser("mesh", help="Broadcast custom packet across P2P mesh")
    mesh_p.add_argument("--msg", required=True, help="Message content")

    search_p = subparsers.add_parser("search", help="Query episodic memory")
    search_p.add_argument("--query", required=True, help="Keyword query")

    args = parser.parse_args()

    if args.command == "chat":
        dispatch_task("chat", {"sender": args.sender, "recipient": args.recipient, "text": args.text})
    elif args.command == "evolve":
        dispatch_task("evolve", {"skill_name": args.name, "code": args.code, "assertion": args.assertion})
    elif args.command == "code":
        dispatch_task("code", {"code": args.snippet})
    elif args.command == "reason":
        dispatch_task("reasoning", {"query": args.query})
    elif args.command == "mesh":
        dispatch_task("mesh", {"msg": args.msg})
    elif args.command == "search":
        search_memory(args.query)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
