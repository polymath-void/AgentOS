use ignore::WalkBuilder;
use rusqlite::{Connection, OpenFlags};
use serde_json::Value;
use std::fs;
use std::path::Path;
use crate::memory::summarizer::HeuristicSummarizer;

pub struct UniversalBridge;

impl UniversalBridge {
    /// Scans the workspace for any foreign agent memory files and synthesizes them.
    pub fn scan_and_ingest(workspace_path: &str) -> String {
        println!("🔍 [Universal Bridge]: Scanning {} for foreign AI memory signatures...", workspace_path);
        
        let mut combined_context = String::new();
        let walker = WalkBuilder::new(workspace_path)
            .max_depth(Some(2)) 
            .hidden(false)
            .build();

        for result in walker.flatten() {
            let path = result.path();
            let file_name = path.file_name().unwrap_or_default().to_string_lossy().to_lowercase();
            
            if file_name.contains("history") || file_name.contains("chat") || 
               file_name.contains("memory") || file_name.contains("brain") {
                   
                let ext = path.extension().unwrap_or_default().to_string_lossy().to_lowercase();
                
                let extracted = match ext.as_str() {
                    "md" | "txt" | "log" => Self::parse_plaintext(path),
                    "json" | "jsonl" => Self::parse_json(path),
                    "db" | "sqlite" | "sqlite3" => Self::parse_sqlite(path),
                    _ => None,
                };

                if let Some(context) = extracted {
                    let summary = HeuristicSummarizer::summarize(&context, 500); // Compress to 500 chars per file
                    combined_context.push_str(&format!("\n--- Context from {} ---\n{}\n", path.display(), summary));
                }
            }
        }

        if combined_context.trim().is_empty() {
            "No foreign agent context detected in this workspace.".to_string()
        } else {
            combined_context
        }
    }

    fn parse_plaintext(path: &Path) -> Option<String> {
        fs::read_to_string(path).ok()
    }

    fn parse_json(path: &Path) -> Option<String> {
        fs::read_to_string(path).ok().and_then(|content| {
            serde_json::from_str::<Value>(&content).ok().map(|v| format!("{:#?}", v))
        })
    }

    fn parse_sqlite(path: &Path) -> Option<String> {
        Connection::open_with_flags(path, OpenFlags::SQLITE_OPEN_READ_ONLY).ok().and_then(|conn| {
            let query = "SELECT role, content FROM messages ORDER BY id DESC LIMIT 5";
            conn.prepare(query).ok().and_then(|mut stmt| {
                let rows = stmt.query_map([], |row| {
                    Ok(format!("[{}]: {}", row.get::<_, String>(0).unwrap_or_default(), row.get::<_, String>(1).unwrap_or_default()))
                }).ok()?;
                Some(rows.flatten().collect::<Vec<_>>().join("\n"))
            })
        })
    }
}
