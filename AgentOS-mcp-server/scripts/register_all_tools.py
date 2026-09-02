
from core.dispatch.dispatch_network import DispatchNetwork
from plugins.tools_manager import ToolsManager

def main():
    tools = ToolsManager("/data/data/com.termux/files/home/Projects/AgentOS/agent-os-hub/plugins")
    dispatch = DispatchNetwork(tools)
    
    tools_to_build = [
        {"name": "web_search", "desc": "Searches the web.", "script": "#!/bin/bash\necho 'Searching web for: $1'"},
        {"name": "file_encrypt", "desc": "Encrypts a file.", "script": "#!/bin/bash\necho 'Encrypting file: $1'"},
        {"name": "code_lint", "desc": "Lints code.", "script": "#!/bin/bash\necho 'Linting directory: $1'"},
        {"name": "metrics_log", "desc": "Logs metrics.", "script": "#!/bin/bash\necho 'Logging metrics: $1'"},
        {"name": "git_status", "desc": "Git status.", "script": "#!/bin/bash\necho 'Git status of: $1'"},
        {"name": "docker_check", "desc": "Docker check.", "script": "#!/bin/bash\necho 'Checking docker: $1'"},
        {"name": "system_info", "desc": "System info.", "script": "#!/bin/bash\necho 'System info: $1'"},
        {"name": "image_convert", "desc": "Converts images.", "script": "#!/bin/bash\necho 'Converting image: $1'"},
        {"name": "backup_sync", "desc": "Syncs backups.", "script": "#!/bin/bash\necho 'Syncing backup: $1'"},
        {"name": "data_compress", "desc": "Compresses data.", "script": "#!/bin/bash\necho 'Compressing data: $1'"}
    ]
    
    for tool in tools_to_build:
        dispatch.route_task("register_tool", {
            "name": tool["name"],
            "description": tool["desc"],
            "script": tool["script"]
        })

if __name__ == "__main__":
    main()
