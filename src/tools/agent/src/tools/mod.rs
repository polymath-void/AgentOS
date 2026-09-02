pub mod builtin;
pub mod context;
pub mod factory;

use std::process::Command;

pub fn execute_shell_command(cmd: &str) -> String {
    println!("⚙️ [Shell Executing]: {}", cmd);
    let output = Command::new("sh")
        .arg("-c")
        .arg(cmd)
        .output();

    match output {
        Ok(out) => {
            let stdout = String::from_utf8_lossy(&out.stdout);
            let stderr = String::from_utf8_lossy(&out.stderr);
            format!("STDOUT:\n{}\nSTDERR:\n{}", stdout, stderr)
        }
        Err(e) => format!("Execution Error: {}", e),
    }
}
