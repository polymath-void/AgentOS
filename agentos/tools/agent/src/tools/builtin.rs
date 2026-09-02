use serde_json::json;
use std::fs::{self, File};
use std::io::Write;
use std::os::unix::fs::PermissionsExt;
use std::path::Path;

/// Returns the JSON schema for built-in tools (execute_shell_command and create_tool)
pub fn get_builtin_schemas() -> Vec<serde_json::Value> {
    vec![
        json!({
            "name": "execute_shell_command",
            "description": "Executes standard bash commands on host system.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "command": { "type": "STRING", "description": "The command string to execute" }
                },
                "required": ["command"]
            }
        }),
        json!({
            "name": "create_tool",
            "description": "Creates and registers a new dynamic tool on the host system for future use.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "tool_name": { "type": "STRING", "description": "Unique identifier for the tool (alphanumeric and underscores)" },
                    "description": { "type": "STRING", "description": "Detailed explanation of what the tool does" },
                    "parameters_schema": {
                        "type": "STRING",
                        "description": "JSON string of parameter properties object conforming to Gemini API schema"
                    },
                    "script_content": { "type": "STRING", "description": "Executable bash/python script content" }
                },
                "required": ["tool_name", "description", "parameters_schema", "script_content"]
            }
        }),
        json!({
            "name": "delegate_task",
            "description": "Spawns a specialized sub-agent to handle a complex, multi-step sub-task in isolation.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "role_description": { "type": "STRING", "description": "The persona/system prompt for the sub-agent (e.g., 'You are an elite Git manager...')" },
                    "objective": { "type": "STRING", "description": "The exact goal the sub-agent must achieve before returning." }
                },
                "required": ["role_description", "objective"]
            }
        }),
        json!({
            "name": "learn_skill",
            "description": "Memorizes a successful methodology, design pattern, or solution so the agent can adapt and use it in future tasks.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "skill_name": { "type": "STRING", "description": "Short name for the skill (e.g., 'avf_vsock_bypass')" },
                    "context_trigger": { "type": "STRING", "description": "When this skill should be applied (e.g., 'When setting up AVF networking')" },
                    "methodology": { "type": "STRING", "description": "The exact steps, code patterns, or compiler flags required." }
                },
                "required": ["skill_name", "context_trigger", "methodology"]
            }
        }),
        json!({
            "name": "verify_submission",
            "description": "Used by a parent agent to formally verify a Micro-Agent's completed work against the original requirements before accepting it.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "submission_text": { "type": "STRING", "description": "The output provided by the micro-agent." },
                    "verification_criteria": { "type": "STRING", "description": "The exact rules it must pass (e.g., 'Must compile without errors')." }
                },
                "required": ["submission_text", "verification_criteria"]
            }
        }),
        json!({
            "name": "scan_universal_memory",
            "description": "Scans a directory for foreign AI agent memory, chat logs, and JSON/SQLite databases, extracting recent context so Polymath can seamlessly continue their work.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "workspace_path": { "type": "STRING", "description": "The directory path to scan for agent signatures (usually '.')" }
                },
                "required": ["workspace_path"]
            }
        }),
        json!({
            "name": "fetch_url",
            "description": "Fetches a web page and extracts the readable text content (stripping HTML).",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "url": { "type": "STRING", "description": "The full HTTP/HTTPS URL to read" }
                },
                "required": ["url"]
            }
        }),
        json!({
            "name": "read_rss",
            "description": "Reads an RSS feed and returns the latest articles and links.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "url": { "type": "STRING", "description": "The RSS feed URL" }
                },
                "required": ["url"]
            }
        }),
        json!({
            "name": "scan_workspace",
            "description": "Recursively maps a directory structure, ignoring hidden files and .gitignore rules, to understand project layout.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "path": { "type": "STRING", "description": "The relative or absolute directory path" },
                    "max_depth": { "type": "INTEGER", "description": "Maximum folder depth to scan (e.g., 2 or 3)" }
                },
                "required": ["path"]
            }
        }),
        json!({
            "name": "git_context",
            "description": "Fetches structured Git information (status, uncommitted diffs, or recent log) for the current repository.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": { "type": "STRING", "description": "Must be 'status', 'diff', or 'log'" }
                },
                "required": ["action"]
            }
        }),
        json!({
            "name": "query_python_brain",
            "description": "Searches the local Python-managed database for codebase context, past errors, or semantic knowledge.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "search_query": { "type": "STRING", "description": "The search query string" }
                },
                "required": ["search_query"]
            }
        })
    ]
}

/// Executes the meta-tool `create_tool` to write a new script and manifest to disk.
pub fn execute_create_tool(
    tools_dir: &Path,
    tool_name: &str,
    description: &str,
    parameters_schema_str: &str,
    script_content: &str,
) -> String {
    if !tools_dir.exists() {
        if let Err(e) = fs::create_dir_all(tools_dir) {
            return format!("Failed to create tools directory: {}", e);
        }
    }

    // Parse parameters schema to ensure valid JSON
    let params_json: serde_json::Value = match serde_json::from_str(parameters_schema_str) {
        Ok(v) => v,
        Err(e) => return format!("Invalid parameters JSON schema: {}", e),
    };

    // Build the function declaration manifest
    let manifest = json!({
        "name": tool_name,
        "description": description,
        "parameters": params_json
    });

    let manifest_path = tools_dir.join(format!("{}.json", tool_name));
    let script_path = tools_dir.join(format!("{}.sh", tool_name));

    // Write manifest JSON
    if let Err(e) = fs::write(&manifest_path, manifest.to_string()) {
        return format!("Failed to write tool manifest: {}", e);
    }

    // Write script content
    let mut file = match File::create(&script_path) {
        Ok(f) => f,
        Err(e) => return format!("Failed to create script file: {}", e),
    };

    if let Err(e) = file.write_all(script_content.as_bytes()) {
        return format!("Failed to write script content: {}", e);
    }

    // Set POSIX execute permissions (0o755)
    let mut perms = match file.metadata() {
        Ok(meta) => meta.permissions(),
        Err(e) => return format!("Failed to read file metadata: {}", e),
    };
    perms.set_mode(0o755);
    if let Err(e) = fs::set_permissions(&script_path, perms) {
        return format!("Failed to set execute permissions: {}", e);
    }

    format!("✅ Tool '{}' successfully created and registered in dynamic registry.", tool_name)
}

pub async fn query_python_brain(query: &str) -> String {
    let url = format!("http://127.0.0.1:8080/search?query={}", query);

    // Reqwest handles this instantly because the connection is local and Python is already warm
    match reqwest::get(&url).await {
        Ok(res) => {
            if let Ok(json_text) = res.text().await {
                json_text
            } else {
                "Error parsing Python daemon response.".to_string()
            }
        },
        Err(e) => format!("Failed to connect to Python Context Daemon: {}", e),
    }
}
