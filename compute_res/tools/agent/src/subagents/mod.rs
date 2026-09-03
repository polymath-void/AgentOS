use crate::memory::ShortTermMemory;
use crate::tools;
use crate::tools::factory::ToolFactory;
use reqwest::Client;
use serde_json::{json, Value};
use std::env;
use std::pin::Pin;
use std::future::Future;

/// Wraps the recursive call in a Boxed Future to satisfy Rust's async recursion rules
pub fn run_subagent<'a>(
    role_description: String,
    objective: String,
    tool_factory: &'a ToolFactory,
    current_depth: u8,
    max_depth: u8,
    use_local_model: bool,
    tx: tokio::sync::mpsc::Sender<String>,
) -> Pin<Box<dyn Future<Output = Result<String, Box<dyn std::error::Error + Send + Sync>>> + Send + 'a>> {
    Box::pin(async move {
        let api_key = env::var("GEMINI_API_KEY").expect("GEMINI_API_KEY must be set");
        let client = Client::new();
        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={}",
            api_key
        );

        let mut st_memory = ShortTermMemory::new(15);
        st_memory.add_turn(json!({ "role": "user", "parts": [{"text": &objective}] }));

        let identity = match current_depth {
            0 => "Polymath (Main Agent)",
            1 => "Master Agent",
            2 => "Sub Agent",
            _ => "Micro Agent",
        };
        
        let delegation_target = match current_depth {
            0 => "Master Agent",
            1 => "Sub Agent",
            _ => "Micro Agent",
        };

        // System prompt reinforces verification at higher levels and implements Zen Metacognition
        let system_instruction = format!(
            "{}\n\n=== ZEN REASONING PROTOCOL & HIERARCHY ===\n\
             You are acting as the {} in our recursive swarm architecture.\n\
             Before taking any action, you must follow the Zen Metacognition loop:\n\
             1. STEP-BACK REFLECTION: What is the underlying core of this request? Are there hidden edge cases?\n\
             2. CHAIN-OF-THOUGHT: Break the solution down into atomic, verifiable steps.\n\
             3. CRITIQUE: Play devil's advocate against your own plan before executing it.\n\n\
             === DELEGATION CHAIN ===\n\
             If the task requires implementation, deep reasoning, or breaking down, you MUST delegate it to a {}.\n\
             The hierarchy flows strictly as: Polymath -> Master -> Sub -> Micro.\n\
             Micro Agents submit their work to Sub Agents -> Sub Agents submit reports to Master Agents -> Master Agents combine all solved reports and submit the actual problem-solving process back up to Polymath.\n\
             If you are Polymath, your final job is to refine the response, implement the codebase, or fix the errors seamlessly to provide the pure solution directly to the user.\n\
             CRITICAL: You must verify the output of your subordinates. If they fail, delegate the task back to them with explicit corrections.",
            role_description, identity, delegation_target
        );

        let prefix = match current_depth {
            0 => "●>",
            1 => "●●",
            2 => "<●●>",
            _ => " <●>",
        };
        let _ = tx.send(format!("{} [{} Spawned]: {}", prefix, identity, role_description)).await;
        loop {
            let mut function_declarations = tools::builtin::get_builtin_schemas();
            function_declarations.extend(tool_factory.load_dynamic_schemas());

            // If we hit max depth, REMOVE the delegate_task tool so Micro-Agents are forced to execute
            if current_depth >= max_depth {
                function_declarations.retain(|f| f["name"] != "delegate_task");
            }

            let tools_payload = json!([{ "functionDeclarations": function_declarations }]);
            let request_body = json!({
                "systemInstruction": { "parts": [{"text": system_instruction}] },
                "contents": st_memory.get_contents(),
                "tools": tools_payload
            });

            if use_local_model {
                let local_url = "http://127.0.0.1:5000/api/infer_sync";
                let local_body = json!({
                    "prompt": format!("{}\n{}", system_instruction, objective)
                });
                let res = client.post(local_url).json(&local_body).send().await?;
                let res_json: Value = res.json().await?;
                if let Some(text) = res_json.get("result") {
                    let _ = tx.send(format!("{} ✔️ [{} Completed Task via Local Engine]", prefix, identity)).await;
                    return Ok(text.as_str().unwrap_or("").to_string());
                } else {
                    return Ok(format!("Local Agent failed to parse API response: {:?}", res_json));
                }
            }

            let res = client.post(&url).json(&request_body).send().await?;
            let res_json: Value = res.json().await?;

            let parts = match res_json["candidates"][0]["content"]["parts"].as_array() {
                Some(p) => p,
                None => return Ok(format!("Agent failed to parse API response.")),
            };

            if let Some(func_call) = parts[0].get("functionCall") {
                let name = func_call["name"].as_str().unwrap();
                let args = &func_call["args"];

                let result = match name {
                    "execute_shell_command" => tools::execute_shell_command(args["command"].as_str().unwrap_or("")),
                    "delegate_task" => {
                        let role = args["role_description"].as_str().unwrap_or("");
                        let sub_objective = args["objective"].as_str().unwrap_or("");
                        
                        let _ = tx.send(format!("{} [Delegating to {}]: {}", prefix, delegation_target, sub_objective)).await;
                        
                        // Recursive Call
                        match run_subagent(role.to_string(), sub_objective.to_string(), tool_factory, current_depth + 1, max_depth, use_local_model, tx.clone()).await {
                            Ok(sub_result) => format!("SUBORDINATE ({}) SUBMISSION FOR VERIFICATION:\n{}", delegation_target, sub_result),
                            Err(e) => format!("{} failed: {}", delegation_target, e)
                        }
                    }
                    custom_tool => tool_factory.execute_dynamic_tool(custom_tool, args),
                };

                st_memory.add_turn(json!({ "role": "model", "parts": [{"functionCall": func_call}] }));
                st_memory.add_turn(json!({ "role": "function", "parts": [{ "functionResponse": { "name": name, "response": {"result": result} } }] }));
                continue;
            } else if let Some(text) = parts[0].get("text") {
                let _ = tx.send(format!("{} ✔️ [{} Completed Task]", prefix, identity)).await;
                return Ok(text.as_str().unwrap().to_string());
            }
        }
    })
}
