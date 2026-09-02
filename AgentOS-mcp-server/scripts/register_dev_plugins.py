
from core.dispatch.dispatch_network import DispatchNetwork
from plugins.tools_manager import ToolsManager

def main():
    tools = ToolsManager("/data/data/com.termux/files/home/Projects/AgentOS/agent-os-hub/plugins")
    dispatch = DispatchNetwork(tools)
    
    dev_plugins = [
        # Coding/Programming
        {"name": "code_refactor", "desc": "Refactors code.", "script": "#!/bin/bash\necho 'Refactoring: $1'"},
        {"name": "unit_test_gen", "desc": "Generates unit tests.", "script": "#!/bin/bash\necho 'Generating tests: $1'"},
        {"name": "debug_tracer", "desc": "Traces code execution.", "script": "#!/bin/bash\necho 'Tracing: $1'"},
        {"name": "dependency_update", "desc": "Updates dependencies.", "script": "#!/bin/bash\necho 'Updating deps...'"},
        
        # System/Linux
        {"name": "linux_sys_check", "desc": "Checks Linux system.", "script": "#!/bin/bash\necho 'Checking Linux...'"},
        {"name": "kernel_mod_list", "desc": "Lists kernel modules.", "script": "#!/bin/bash\necho 'Listing modules...'"},
        {"name": "firewall_config", "desc": "Configures firewall.", "script": "#!/bin/bash\necho 'Configuring FW...'"},
        
        # Android
        {"name": "adb_cmd", "desc": "Runs ADB command.", "script": "#!/bin/bash\necho 'Running ADB: $1'"},
        {"name": "logcat_capture", "desc": "Captures logcat.", "script": "#!/bin/bash\necho 'Capturing logcat...'"},
        {"name": "pkg_manager", "desc": "Manages Android pkgs.", "script": "#!/bin/bash\necho 'Pkg manager: $1'"},
        
        # GitHub/Dev
        {"name": "git_commit_auto", "desc": "Auto-commits changes.", "script": "#!/bin/bash\necho 'Committing: $1'"},
        {"name": "git_branch_manage", "desc": "Manages git branches.", "script": "#!/bin/bash\necho 'Managing branches...'"},
        {"name": "github_issue_track", "desc": "Tracks issues.", "script": "#!/bin/bash\necho 'Tracking issue: $1'"},
        {"name": "repo_sync", "desc": "Syncs repository.", "script": "#!/bin/bash\necho 'Syncing repo...'"},
        
        # System Dev
        {"name": "build_compiler", "desc": "Compiles project.", "script": "#!/bin/bash\necho 'Compiling: $1'"},
        {"name": "binary_analyzer", "desc": "Analyzes binaries.", "script": "#!/bin/bash\necho 'Analyzing binary: $1'"}
    ]
    
    for tool in dev_plugins:
        dispatch.route_task("register_tool", {
            "name": tool["name"],
            "description": tool["desc"],
            "script": tool["script"]
        })

if __name__ == "__main__":
    main()
