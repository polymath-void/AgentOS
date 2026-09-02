use serde_json::Value;
use std::fs;
use std::path::PathBuf;
use std::process::Command;

pub struct ToolFactory {
    tools_dir: PathBuf,
}

impl ToolFactory {
    pub fn new(tools_dir: PathBuf) -> Self {
        if !tools_dir.exists() {
            let _ = fs::create_dir_all(&tools_dir);
        }
        Self { tools_dir }
    }

    /// Scans ~/.polymath_agent/tools/ and loads all custom tool JSON schemas
    pub fn load_dynamic_schemas(&self) -> Vec<Value> {
        let mut schemas = Vec::new();

        if let Ok(entries) = fs::read_dir(&self.tools_dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.extension().and_then(|s| s.to_str()) == Some("json") {
                    if let Ok(content) = fs::read_to_string(&path) {
                        if let Ok(json_val) = serde_json::from_str::<Value>(&content) {
                            schemas.push(json_val);
                        }
                    }
                }
            }
        }

        schemas
    }

    /// Executes a dynamic custom tool script passing arguments as JSON string input
    pub fn execute_dynamic_tool(&self, name: &str, args: &Value) -> String {
        let script_path = self.tools_dir.join(format!("{}.sh", name));

        if !script_path.exists() {
            return format!("Error: Script for dynamic tool '{}' not found at {:?}", name, script_path);
        }

        let args_str = args.to_string();

        let output = Command::new(&script_path)
            .arg(&args_str)
            .output();

        match output {
            Ok(out) => {
                let stdout = String::from_utf8_lossy(&out.stdout);
                let stderr = String::from_utf8_lossy(&out.stderr);
                format!("STDOUT:\n{}\nSTDERR:\n{}", stdout, stderr)
            }
            Err(e) => format!("Dynamic Tool Execution Error: {}", e),
        }
    }
}
