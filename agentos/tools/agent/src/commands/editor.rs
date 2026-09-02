use crossterm::terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen};
use crossterm::ExecutableCommand;
use std::io;
use std::process::Command;
use std::fs;

pub fn open_external_editor() -> Option<String> {
    // 1. Suspend the TUI
    disable_raw_mode().unwrap();
    io::stdout().execute(LeaveAlternateScreen).unwrap();

    let temp_file = "/data/data/com.termux/files/usr/tmp/polymath_prompt.txt";
    fs::write(temp_file, "# Write your complex objective here. Save and exit when done.\n").unwrap();

    // 2. Launch Nano/Vim
    let editor = std::env::var("EDITOR").unwrap_or_else(|_| "nano".to_string());
    Command::new(editor)
        .arg(temp_file)
        .status()
        .expect("Failed to open external editor");

    // 3. Read the result and clean up
    let content = fs::read_to_string(temp_file).unwrap_or_default();
    let _ = fs::remove_file(temp_file);

    // 4. Resume the TUI
    enable_raw_mode().unwrap();
    io::stdout().execute(EnterAlternateScreen).unwrap();

    let clean_content = content.replace("# Write your complex objective here. Save and exit when done.\n", "").trim().to_string();
    
    if clean_content.is_empty() { None } else { Some(clean_content) }
}
