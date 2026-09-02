
from core.dispatch.dispatch_network import DispatchNetwork
from plugins.tools_manager import ToolsManager

def main():
    tools = ToolsManager("/data/data/com.termux/files/home/Projects/AgentOS/agent-os-hub/plugins")
    dispatch = DispatchNetwork(tools)
    
    new_plugins = [
        {"name": "text_summarize", "desc": "Summarizes text inputs.", "script": "#!/bin/bash\necho 'Summarizing: $1'"},
        {"name": "json_validate", "desc": "Validates JSON format.", "script": "#!/bin/bash\necho 'Validating JSON: $1'"},
        {"name": "regex_search", "desc": "Searches text using regex.", "script": "#!/bin/bash\necho 'Regex search: $1'"},
        {"name": "file_diff", "desc": "Compares two files.", "script": "#!/bin/bash\necho 'Diffing: $1'"},
        {"name": "date_convert", "desc": "Converts date formats.", "script": "#!/bin/bash\necho 'Converting date: $1'"},
        {"name": "port_scan", "desc": "Scans local ports.", "script": "#!/bin/bash\necho 'Scanning ports...'"},
        {"name": "process_list", "desc": "Lists active processes.", "script": "#!/bin/bash\necho 'Listing processes...'"},
        {"name": "disk_usage", "desc": "Checks disk usage.", "script": "#!/bin/bash\necho 'Checking disk...'"},
        {"name": "network_status", "desc": "Checks network status.", "script": "#!/bin/bash\necho 'Checking network...'"},
        {"name": "pkg_install", "desc": "Installs a package.", "script": "#!/bin/bash\necho 'Installing package: $1'"},
        {"name": "user_add", "desc": "Adds a user.", "script": "#!/bin/bash\necho 'Adding user: $1'"},
        {"name": "log_tail", "desc": "Tails a log file.", "script": "#!/bin/bash\necho 'Tailing log: $1'"},
        {"name": "url_encode", "desc": "URL encodes strings.", "script": "#!/bin/bash\necho 'Encoding URL: $1'"},
        {"name": "base64_decode", "desc": "Base64 decodes data.", "script": "#!/bin/bash\necho 'Decoding Base64: $1'"},
        {"name": "hash_file", "desc": "Hashes a file.", "script": "#!/bin/bash\necho 'Hashing file: $1'"},
        {"name": "cron_list", "desc": "Lists cron jobs.", "script": "#!/bin/bash\necho 'Listing cron...'"},
        {"name": "env_dump", "desc": "Dumps environment vars.", "script": "#!/bin/bash\necho 'Dumping env...'"},
        {"name": "service_restart", "desc": "Restarts a service.", "script": "#!/bin/bash\necho 'Restarting: $1'"},
        {"name": "path_resolve", "desc": "Resolves file paths.", "script": "#!/bin/bash\necho 'Resolving path: $1'"},
        {"name": "uuid_gen", "desc": "Generates a UUID.", "script": "#!/bin/bash\necho 'Generating UUID...'"},
        {"name": "random_string", "desc": "Generates random string.", "script": "#!/bin/bash\necho 'Generating random string...'"},
        {"name": "sleep_task", "desc": "Sleeps for duration.", "script": "#!/bin/bash\necho 'Sleeping: $1'"},
        {"name": "time_check", "desc": "Checks current time.", "script": "#!/bin/bash\necho 'Time is...'"},
        {"name": "uptime_check", "desc": "Checks system uptime.", "script": "#!/bin/bash\necho 'Uptime is...'"},
        {"name": "mem_check", "desc": "Checks memory usage.", "script": "#!/bin/bash\necho 'Checking memory...'"}
    ]
    
    for tool in new_plugins:
        dispatch.route_task("register_tool", {
            "name": tool["name"],
            "description": tool["desc"],
            "script": tool["script"]
        })

if __name__ == "__main__":
    main()
