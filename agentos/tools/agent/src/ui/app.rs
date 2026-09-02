use tui_input::Input;
use std::env;

pub enum AgentStatus {
    Idle,
    Thinking(String),      // e.g., "Master Agent Planning..."
    ExecutingTool(String), // e.g., "Sub-Agent Running cargo check"
    Distilling,            // Local prompt compilation
    Downloading(f64),      // Model download progress
}

pub enum TrustLevel {
    Trusted,   // Agent can execute shell scripts and edit files freely
    Untrusted, // Agent must prompt user via UI before file I/O or execution
}

pub struct Config {
    pub active_model: String,     // e.g., "gemini-2.5-flash"
    pub theme_primary: [u8; 3],   // RGB color for borders
    pub theme_text: [u8; 3],      // RGB color for text
    pub ui_style: String,         // "minimal", "hacker", "clean"
    pub auto_refine_prompts: bool,// Local AI prompt compilation
    pub use_local_model: bool,    // Feature flag
    pub max_depth: u8,            // Max recursive agent depth
    pub prune_memory: bool,       // Aggressive context pruning
    pub timeout: u16,             // API timeout in seconds
}

pub struct App {
    pub input: Input,
    pub messages: Vec<String>,
    pub status: AgentStatus,
    pub active_sub_agents: Vec<String>,
    pub cwd: String,              // Current Working Directory
    pub trust_level: TrustLevel,
    pub loaded_tools_count: usize,
    pub config: Config,
    pub should_quit: bool,
    pub scroll: usize,
    pub tick: usize,
    pub suggestion_index: usize,
}

impl App {
    pub fn new() -> Self {
        let art = r#"
  ____       _                       _   _    
 |  _ \ ___ | |_   _ _ __ ___   __ _| |_| |__ 
 | |_) / _ \| | | | | '_ ` _ \ / _` | __| '_ \
 |  __/ (_) | | |_| | | | | | | (_| | |_| | | 
 |_|   \___/|_|\__, |_| |_| |_|\__,_|\__|_| |_
               |___/                          "#;
        let cwd = env::current_dir().unwrap_or_default().display().to_string();
        Self {
            input: Input::default(),
            messages: vec![art.to_string(), "🚀 Welcome to the Polymath-Void Swarm.".to_string()],
            status: AgentStatus::Idle,
            active_sub_agents: Vec::new(),
            cwd,
            trust_level: TrustLevel::Untrusted, // Default to safe
            loaded_tools_count: 5, // Built-ins
            config: Config {
                active_model: "gemini-2.5-flash".to_string(),
                theme_primary: [0, 255, 128], // Hacker Green
                theme_text: [200, 200, 200],  // Light Grey
                ui_style: "hacker".to_string(),
                auto_refine_prompts: false, // Default to off
                use_local_model: false,       // 🔴 Disabled by default
                max_depth: 3,
                prune_memory: true,
                timeout: 30,
            },
            should_quit: false,
            scroll: 0,
            tick: 0,
            suggestion_index: 0,
        }
    }

    pub fn get_suggestions(&self) -> Vec<&'static str> {
        let input_text = self.input.value();
        if !input_text.starts_with('/') {
            return vec![];
        }
        let all_commands = vec![
            "/config model ",
            "/config trust true",
            "/config trust false",
            "/config local_model true",
            "/config local_model false",
            "/config api ",
            "/config theme matrix",
            "/config theme dracula",
            "/config theme synthwave",
            "/config max_depth 3",
            "/config prune_memory true",
            "/config timeout 30",
            "/editor",
            "/agents",
            "/plan",
            "/implement",
            "/suggestions",
        ];
        all_commands.into_iter()
            .filter(|cmd| cmd.starts_with(input_text) && *cmd != input_text)
            .collect()
    }
}
