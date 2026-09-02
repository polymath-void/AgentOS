#[derive(Debug)]
pub enum CommandAction {
    AgentPrompt(String),     // Standard message to LLM
    SetModel(String),        // /config model gemini-2.5-pro
    SetTrust(bool),          // /config trust true
    SetLocalModel(bool),     // /config local_model true
    SetMaxDepth(u8),         // /config max_depth 3
    SetPruneMemory(bool),    // /config prune_memory true
    SetTimeout(u16),         // /config timeout 30
    SetApi(String),          // /config api KEY
    SetTheme(String),        // /config theme name
    LaunchEditor,            // /editor (opens Nano/Vim)
    ShowAgents,              // /agents (lists master, sub, micro)
    TriggerWorkflow(String), // /plan, /implement, /schedule
    ShowSuggestions,         // /suggestions
}

pub fn parse_input(input: &str) -> CommandAction {
    if !input.starts_with('/') {
        return CommandAction::AgentPrompt(input.to_string());
    }

    let parts: Vec<&str> = input.split_whitespace().collect();
    match parts[0] {
        "/config" => {
            if parts.len() > 2 && parts[1] == "model" {
                CommandAction::SetModel(parts[2].to_string())
            } else if parts.len() > 2 && parts[1] == "trust" {
                CommandAction::SetTrust(parts[2] == "true")
            } else if parts.len() > 2 && parts[1] == "local_model" {
                CommandAction::SetLocalModel(parts[2] == "true")
            } else if parts.len() > 2 && parts[1] == "max_depth" {
                if let Ok(depth) = parts[2].parse::<u8>() {
                    CommandAction::SetMaxDepth(depth)
                } else {
                    CommandAction::AgentPrompt("Invalid max_depth value".to_string())
                }
            } else if parts.len() > 2 && parts[1] == "prune_memory" {
                CommandAction::SetPruneMemory(parts[2] == "true")
            } else if parts.len() > 2 && parts[1] == "timeout" {
                if let Ok(timeout) = parts[2].parse::<u16>() {
                    CommandAction::SetTimeout(timeout)
                } else {
                    CommandAction::AgentPrompt("Invalid timeout value".to_string())
                }
            } else if parts.len() > 2 && parts[1] == "api" {
                CommandAction::SetApi(parts[2].to_string())
            } else if parts.len() > 2 && parts[1] == "theme" {
                CommandAction::SetTheme(parts[2].to_string())
            } else {
                CommandAction::AgentPrompt("Invalid config command".to_string())
            }
        }
        "/editor" => CommandAction::LaunchEditor,
        "/agents" => CommandAction::ShowAgents,
        "/plan" => CommandAction::TriggerWorkflow("INITIALIZE_PLANNING_PHASE".to_string()),
        "/implement" => CommandAction::TriggerWorkflow("EXECUTE_IMPLEMENTATION".to_string()),
        "/suggestions" => CommandAction::ShowSuggestions,
        _ => CommandAction::AgentPrompt(input.to_string()),
    }
}
