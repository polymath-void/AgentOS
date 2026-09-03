#[cfg(test)]
mod tests {
    use crate::ui::app::Config;
    use crate::commands::router::{parse_input, CommandAction};

    #[test]
    fn test_config_default_state() {
        let config = Config {
            active_model: "gemini-2.5-flash".to_string(),
            theme_primary: [0, 255, 128],
            theme_text: [200, 200, 200],
            ui_style: "hacker".to_string(),
            auto_refine_prompts: false,
            use_local_model: false,
        };
        assert!(!config.use_local_model);
    }

    #[test]
    fn test_parse_local_model_command() {
        let input = "/config local_model true";
        let action = parse_input(input);
        match action {
            CommandAction::SetLocalModel(val) => assert!(val),
            _ => panic!("Expected SetLocalModel, got {:?}", action),
        }
    }
}
