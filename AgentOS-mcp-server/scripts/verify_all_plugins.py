
from core.dispatch.dispatch_network import DispatchNetwork
from plugins.tools_manager import ToolsManager

def main():
    tools = ToolsManager("/data/data/com.termux/files/home/Projects/AgentOS/agent-os-hub/plugins")
    dispatch = DispatchNetwork(tools)
    
    # List of all registered plugins to test
    plugins_to_test = [
        "text_summarize", "json_validate", "regex_search", "file_diff", "date_convert",
        "port_scan", "process_list", "disk_usage", "network_status", "pkg_install",
        "user_add", "log_tail", "url_encode", "base64_decode", "hash_file",
        "cron_list", "env_dump", "service_restart", "path_resolve", "uuid_gen",
        "random_string", "sleep_task", "time_check", "uptime_check", "mem_check",
        "code_inspector", "code_analyzer", "code_researcher", "code_verifier", 
        "logic_manager", "algo_writer", "dir_manager", "doc_generator",
        "code_refactor", "unit_test_gen", "debug_tracer", "dependency_update",
        "linux_sys_check", "kernel_mod_list", "firewall_config", "adb_cmd",
        "logcat_capture", "pkg_manager", "git_commit_auto", "git_branch_manage",
        "github_issue_track", "repo_sync", "build_compiler", "binary_analyzer"
    ]
    
    print(f"--- Starting Comprehensive Plugin Verification ({len(plugins_to_test)} plugins) ---")
    
    for tool in plugins_to_test:
        print(f"\nVerifying: {tool}")
        # Test in simulation mode first
        dispatch.route_task("execute", {"name": tool, "args": "test_arg", "mode": "simulate"})
        
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    main()
