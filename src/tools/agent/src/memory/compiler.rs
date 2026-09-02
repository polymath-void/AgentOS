use std::process::Command;

pub struct PromptCompiler;

impl PromptCompiler {
    pub async fn ensure_model_exists(model_path: &str) -> Result<(), String> {
        // Simple placeholder for now: assume download logic exists or will be added
        if std::path::Path::new(model_path).exists() {
            Ok(())
        } else {
            Err("Model not found at specified path.".to_string())
        }
    }

    /// Refines the user's input by grounding it in the agent's current active memory.
    pub fn refine_prompt(
        raw_input: &str, 
        active_context: &str, 
        model_path: &str, 
        cli_path: &str
    ) -> String {
        println!("🧠 [Local Compiler]: Grounding and refining prompt...");

        // The instruction forces the local model to act as a contextual translator.
        let compiler_instruction = "\
            You are a Prompt Compiler operating as a pre-flight router. \
            Below is the ACTIVE MEMORY of the AI system, followed by the user's RAW INPUT. \
            Your job is to rewrite the raw input into a dense, imperative command for the Master AI. \
            CRITICAL RULES: \
            1. Resolve all ambiguous pronouns (e.g., 'it', 'the file') using the ACTIVE MEMORY. \
            2. State the exact file paths, tools, or errors mentioned recently. \
            3. Remove conversational filler. Output ONLY the refined technical command.";

        // Construct the context-aware payload
        let full_prompt = format!(
            "{}\n\n=== ACTIVE MEMORY ===\n{}\n\n=== RAW INPUT ===\n{}\n\n=== REFINED COMMAND ===",
            compiler_instruction, 
            active_context, 
            raw_input
        );

        let output = Command::new(cli_path)
            .arg("-m").arg(model_path)
            .arg("-p").arg(&full_prompt)
            .arg("-n").arg("250") 
            .arg("--temp").arg("0.1") 
            .arg("--log-disable") 
            .output();

        match output {
            Ok(out) => {
                let refined_text = String::from_utf8_lossy(&out.stdout).trim().to_string();
                if refined_text.is_empty() {
                    raw_input.to_string()
                } else {
                    println!("✨ [Local Compiler]: Contextual distillation complete.");
                    refined_text
                }
            }
            Err(e) => {
                println!("⚠️ [Local Compiler]: Execution failed ({}). Using raw input.", e);
                raw_input.to_string()
            }
        }
    }
}
