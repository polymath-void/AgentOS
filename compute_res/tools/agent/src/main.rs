use crossterm::{
    event::{self, Event, KeyCode},
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
    ExecutableCommand,
};
use ratatui::{backend::CrosstermBackend, Terminal};
use std::io;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use tokio::sync::{mpsc, Mutex};
use tui_input::backend::crossterm::EventHandler;

mod commands;
mod memory;
mod subagents;
mod tools;
mod ui;
#[cfg(test)]
mod tests;

use commands::router::{parse_input, CommandAction};
use memory::{LongTermMemory, ShortTermMemory, compiler::PromptCompiler};
use tools::factory::ToolFactory;
use ui::app::{App, AgentStatus, TrustLevel};
use ui::render::draw_dashboard;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    
    // Setup Terminal
    // Attempt robust initialization, warn if it fails but don't crash
    if let Err(e) = enable_raw_mode() {
        eprintln!("Warning: Could not enable raw mode ({}). UI may be limited.", e);
    }
    io::stdout().execute(EnterAlternateScreen)?;
    
    let mut terminal = Terminal::new(CrosstermBackend::new(io::stdout()))?;


#[derive(Clone, Debug)]
pub struct AgentRequest {
    pub prompt: String,
    pub use_local_model: bool,
    pub max_depth: u8,
}

    // Channels for UI <-> Agent communication
    let (tx_ui_to_agent, mut rx_ui_to_agent) = mpsc::channel::<AgentRequest>(32);
    let (tx_agent_to_ui, mut rx_agent_to_ui) = mpsc::channel::<String>(100);

    let mut app = App::new();
    let current_dir = app.cwd.clone();
    
    // Core systems need to be accessible within the UI Loop
    let tools_dir = PathBuf::from(&current_dir).join(".polymath_agent").join("tools");
    let lt_memory = Arc::new(LongTermMemory::new("polymath_agent_memory.db").unwrap());
    let st_memory = Arc::new(Mutex::new(ShortTermMemory::new(20)));

    // Spawn the background ReAct Orchestrator task
    let _lt_memory_bg = lt_memory.clone();
    let _st_memory_bg = st_memory.clone();
    let tools_dir_bg = tools_dir.clone();
    let tx_agent_to_ui_bg = tx_agent_to_ui.clone();

    tokio::spawn(async move {
        let tool_factory = ToolFactory::new(tools_dir_bg);
        while let Some(req) = rx_ui_to_agent.recv().await {
            let _ = tx_agent_to_ui_bg.send(format!("[System]: Agent processing started...")).await;
            
            let result = subagents::run_subagent(
                "Primary Orchestrator".to_string(),
                req.prompt.clone(),
                &tool_factory,
                0,
                req.max_depth,
                req.use_local_model,
                tx_agent_to_ui_bg.clone()
            ).await;
            
            match result {
                Ok(response) => {
                    let _ = tx_agent_to_ui_bg.send(format!("●> {}", response)).await;
                    
                    // Automatically compress and save to Long-Term SQLite Memory
                    let timestamp = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
                    let mem_key = format!("Interaction_{}", timestamp);
                    let memory_payload = format!("Prompt: {}\nResolution: {}", req.prompt, response);
                    
                    if let Err(e) = _lt_memory_bg.set_fact("Archived_Resolutions", &mem_key, &memory_payload) {
                        let _ = tx_agent_to_ui_bg.send(format!("[System Error]: Failed to save memory - {}", e)).await;
                    } else {
                        let _ = tx_agent_to_ui_bg.send("[System]: 🧠 Memory securely committed to Long-Term Storage.".to_string()).await;
                    }
                }
                Err(e) => {
                    let _ = tx_agent_to_ui_bg.send(format!("[Agent Error]: {}", e)).await;
                }
            }
        }
    });

    // Start Python Context Daemon
    std::process::Command::new("uv")
        .arg("run")
        .arg("context_daemon.py")
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .spawn()
        .expect("Failed to start Python context daemon");

    // The Main UI Render Loop
    loop {
        // Check for new messages from the background agent
        while let Ok(msg) = rx_agent_to_ui.try_recv() {
            app.messages.push(msg);
        }

        // Draw the highly customized layout
        terminal.draw(|f| draw_dashboard(f, &app))?;

        // Handle Keyboard Events natively
        if event::poll(std::time::Duration::from_millis(16))? {
            if let Event::Key(key) = event::read()? {
                match key.code {
                    KeyCode::Esc => { 
                        app.input.reset();
                        app.suggestion_index = 0;
                    }
                    KeyCode::Char('c') if key.modifiers.contains(event::KeyModifiers::CONTROL) => {
                        app.should_quit = true;
                    }
                    KeyCode::PageUp => { app.scroll = app.scroll.saturating_add(5); }
                    KeyCode::PageDown => { app.scroll = app.scroll.saturating_sub(5); }
                    KeyCode::Up if key.modifiers.contains(event::KeyModifiers::CONTROL) => { app.scroll = app.scroll.saturating_add(1); }
                    KeyCode::Down if key.modifiers.contains(event::KeyModifiers::CONTROL) => { app.scroll = app.scroll.saturating_sub(1); }
                    KeyCode::Up => {
                        let suggestions = app.get_suggestions();
                        if !suggestions.is_empty() {
                            app.suggestion_index = app.suggestion_index.saturating_sub(1);
                        }
                    }
                    KeyCode::Down => {
                        let suggestions = app.get_suggestions();
                        if !suggestions.is_empty() {
                            app.suggestion_index = (app.suggestion_index + 1) % suggestions.len();
                        }
                    }
                    KeyCode::Tab => {
                        let suggestions = app.get_suggestions();
                        if !suggestions.is_empty() {
                            let selected = suggestions[app.suggestion_index % suggestions.len()];
                            app.input = tui_input::Input::new(selected.to_string());
                            app.suggestion_index = 0;
                        }
                    }
                    KeyCode::Enter => {
                        let suggestions = app.get_suggestions();
                        if !suggestions.is_empty() {
                            let selected = suggestions[app.suggestion_index % suggestions.len()];
                            app.input = tui_input::Input::new(selected.to_string());
                            app.suggestion_index = 0;
                            continue;
                        }
                        
                        app.scroll = 0;
                        let raw_req = app.input.value().to_string();
                        app.input.reset();
                        app.suggestion_index = 0;

                        if !raw_req.is_empty() {
                            app.messages.push(format!("> {}", raw_req));

                            // Process command before dispatching to Agent
                            match parse_input(&raw_req) {
                                CommandAction::AgentPrompt(req) => {
                                    let final_req = req;

                                    let model_path = "/data/data/com.termux/files/home/models/phi-3-mini-q4.gguf";

                                    if app.config.use_local_model && Path::new(model_path).exists() && !raw_req.starts_with('/') {
                                        app.status = AgentStatus::Distilling;
                                        terminal.draw(|f| draw_dashboard(f, &app))?; // Force update

                                        // 1. Gather Long-Term Facts
                                        let facts = lt_memory.get_formatted_facts().unwrap_or_default();

                                        // 2. Gather Short-Term History
                                        let recent_history = st_memory.lock().await.get_recent_turns_as_string(3); 

                                        // 3. Combine into a lightweight context snapshot
                                        let active_context = format!("FACTS:\n{}\n\nRECENT CHAT:\n{}", facts, recent_history);

                                        // 4. Pass the context and the raw input to the local compiler
                                        let tx_agent = tx_ui_to_agent.clone();
                                        let final_req_clone = final_req.clone();
                                        let use_local_model = app.config.use_local_model;
                                        let max_depth = app.config.max_depth;
                                        tokio::spawn(async move {
                                            let cli_path = "/data/data/com.termux/files/home/Projects/local/native_ai_engine/build/native_ai_engine";
                                            let fallback = final_req_clone.clone();
                                            let refined_req = tokio::task::spawn_blocking(move || {
                                                PromptCompiler::refine_prompt(&final_req_clone, &active_context, model_path, cli_path)
                                            })
                                            .await
                                            .unwrap_or(fallback);
                                            let _ = tx_agent.send(AgentRequest {
                                                prompt: refined_req,
                                                use_local_model,
                                                max_depth
                                            }).await;
                                        });
                                        app.status = AgentStatus::Idle;
                                        app.messages.push(format!("[System (Refined)]: Distillation via local model queued."));
                                    } else {
                                        let _ = tx_ui_to_agent.send(AgentRequest {
                                            prompt: final_req,
                                            use_local_model: app.config.use_local_model,
                                            max_depth: app.config.max_depth
                                        }).await;
                                    }
                                }
                                CommandAction::LaunchEditor => {
                                    if let Some(edited_prompt) = commands::editor::open_external_editor() {
                                        app.messages.push("[System]: Editor content ingested.".to_string());
                                        let _ = tx_ui_to_agent.send(AgentRequest {
                                            prompt: edited_prompt,
                                            use_local_model: app.config.use_local_model,
                                            max_depth: app.config.max_depth
                                        }).await;
                                    }
                                }
                                CommandAction::SetLocalModel(enable) => {
                                    app.config.use_local_model = enable;
                                    
                                    if enable {
                                        let model_path = "/data/data/com.termux/files/home/models/phi-3-mini-q4.gguf";
                                        
                                        if !Path::new(model_path).exists() {
                                            app.messages.push("📥 [System]: Local model missing. Downloading 2.3GB GGUF in the background...".to_string());
                                            
                                            let tx_agent = tx_agent_to_ui.clone();
                                            tokio::spawn(async move {
                                                match PromptCompiler::ensure_model_exists(model_path).await {
                                                    Ok(_) => {
                                                        let _ = tx_agent.send("✅ [System]: Local model downloaded and ready for prompt distillation.".to_string()).await;
                                                    }
                                                    Err(e) => {
                                                        let _ = tx_agent.send(format!("❌ [System]: Background download failed: {}", e)).await;
                                                    }
                                                }
                                            });
                                        } else {
                                            app.messages.push("⚡ [System]: Local edge model enabled and ready.".to_string());
                                        }
                                    } else {
                                        app.messages.push("🛑 [System]: Local edge model disabled. Routing raw prompts to cloud.".to_string());
                                    }
                                }
                                CommandAction::SetMaxDepth(depth) => {
                                    app.config.max_depth = depth;
                                    app.messages.push(format!("> [System]: Agent max depth set to {}", depth));
                                }
                                CommandAction::SetPruneMemory(val) => {
                                    app.config.prune_memory = val;
                                    app.messages.push(format!("> [System]: Context memory pruning set to {}", val));
                                }
                                CommandAction::SetTimeout(val) => {
                                    app.config.timeout = val;
                                    app.messages.push(format!("> [System]: API timeout set to {} seconds", val));
                                }
                                CommandAction::SetTrust(val) => {
                                    app.trust_level = if val { TrustLevel::Trusted } else { TrustLevel::Untrusted };
                                    app.messages.push(format!("[System]: Trust level set to {:?}", val));
                                }
                                CommandAction::SetApi(key) => {
                                    std::env::set_var("GEMINI_API_KEY", &key);
                                    use std::io::Write;
                                    if let Ok(mut file) = std::fs::OpenOptions::new().create(true).write(true).truncate(true).open(".env") {
                                        let _ = writeln!(file, "GEMINI_API_KEY={}", key);
                                    }
                                    app.messages.push("> [System]: API Key securely stored for future boots.".to_string());
                                }
                                CommandAction::SetTheme(name) => {
                                    match name.as_str() {
                                        "matrix" => {
                                            app.config.theme_primary = [0, 255, 0];
                                            app.config.theme_text = [200, 255, 200];
                                            app.messages.push("> [System]: Theme set to Matrix".to_string());
                                        }
                                        "dracula" => {
                                            app.config.theme_primary = [255, 121, 198];
                                            app.config.theme_text = [248, 248, 242];
                                            app.messages.push("> [System]: Theme set to Dracula".to_string());
                                        }
                                        "synthwave" => {
                                            app.config.theme_primary = [255, 0, 102];
                                            app.config.theme_text = [0, 255, 255];
                                            app.messages.push("> [System]: Theme set to Synthwave".to_string());
                                        }
                                        _ => {
                                            app.messages.push(format!("> [System]: Unknown theme '{}'", name));
                                        }
                                    }
                                }
                                CommandAction::ShowAgents => {
                                    app.messages.push(format!("[System]: Active swarm: {:?}", app.active_sub_agents));
                                }
                                _ => {
                                    app.messages.push(format!("[System]: Command not yet implemented."));
                                }
                            }
                        }
                    }
                    _ => { 
                        app.input.handle_event(&Event::Key(key)); 
                    }
                }
            }
        }

        if app.should_quit {
            break;
        }
    }

    // Teardown Terminal
    disable_raw_mode()?;
    io::stdout().execute(LeaveAlternateScreen)?;
    Ok(())
}
