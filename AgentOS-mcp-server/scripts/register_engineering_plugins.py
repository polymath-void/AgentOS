
from core.dispatch.dispatch_network import DispatchNetwork
from plugins.tools_manager import ToolsManager

def main():
    tools = ToolsManager("/data/data/com.termux/files/home/Projects/AgentOS/agent-os-hub/plugins")
    dispatch = DispatchNetwork(tools)
    
    specialized_plugins = [
        {"name": "code_inspector", "desc": "Inspects code for style/issues.", "script": "#!/bin/bash\necho 'Inspecting code in: $1'"},
        {"name": "code_analyzer", "desc": "Performs static analysis.", "script": "#!/bin/bash\necho 'Analyzing code: $1'"},
        {"name": "code_researcher", "desc": "Researches dependencies/libs.", "script": "#!/bin/bash\necho 'Researching lib: $1'"},
        {"name": "code_verifier", "desc": "Verifies code logic/types.", "script": "#!/bin/bash\necho 'Verifying code: $1'"},
        {"name": "logic_manager", "desc": "Manages complex logic flows.", "script": "#!/bin/bash\necho 'Managing logic: $1'"},
        {"name": "algo_writer", "desc": "Writes algorithmic solutions.", "script": "#!/bin/bash\necho 'Writing algo for: $1'"},
        {"name": "dir_manager", "desc": "Organizes codebase structure.", "script": "#!/bin/bash\necho 'Managing directory: $1'"},
        {"name": "doc_generator", "desc": "Generates documentation.", "script": "#!/bin/bash\necho 'Generating docs for: $1'"}
    ]
    
    for tool in specialized_plugins:
        dispatch.route_task("register_tool", {
            "name": tool["name"],
            "description": tool["desc"],
            "script": tool["script"]
        })

if __name__ == "__main__":
    main()
