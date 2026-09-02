use ignore::WalkBuilder;
use scraper::{Html, Selector};
use std::process::Command;

/// Fetches a URL and extracts raw text, stripping away the HTML DOM
pub async fn fetch_url(url: &str) -> String {
    println!("🌐 [Agent Browsing]: {}", url);
    match reqwest::get(url).await {
        Ok(response) => {
            if let Ok(html_content) = response.text().await {
                let document = Html::parse_document(&html_content);
                // Select body to avoid head tags, scripts, etc.
                let selector = Selector::parse("body").unwrap();
                let mut extracted_text = String::new();
                
                for element in document.select(&selector) {
                    let text = element.text().collect::<Vec<_>>().join(" ");
                    extracted_text.push_str(&text);
                }
                
                // Truncate to avoid blowing up the token context (e.g., max 10,000 chars)
                let max_len = 10000;
                if extracted_text.len() > max_len {
                    format!("{}...\n\n[Content truncated for context limits]", &extracted_text[..max_len])
                } else {
                    extracted_text
                }
            } else {
                "Error: Failed to read HTML text.".to_string()
            }
        }
        Err(e) => format!("Network Error: {}", e),
    }
}

/// Parses an RSS XML feed into readable summaries
pub async fn read_rss(url: &str) -> String {
    println!("📡 [Agent Fetching RSS]: {}", url);
    match reqwest::get(url).await {
        Ok(response) => {
            if let Ok(bytes) = response.bytes().await {
                if let Ok(channel) = rss::Channel::read_from(&bytes[..]) {
                    let mut output = format!("RSS Feed: {}\n\n", channel.title);
                    for item in channel.items.iter().take(10) { // Limit to top 10
                        let title = item.title.as_deref().unwrap_or("No Title");
                        let link = item.link.as_deref().unwrap_or("No Link");
                        output.push_str(&format!("- {} ({})\n", title, link));
                    }
                    output
                } else {
                    "Error: Failed to parse RSS XML.".to_string()
                }
            } else {
                "Error: Failed to download RSS payload.".to_string()
            }
        }
        Err(e) => format!("Network Error: {}", e),
    }
}

/// Scans the directory tree efficiently, respecting .gitignore
pub fn scan_workspace(path: &str, max_depth: Option<usize>) -> String {
    println!("📂 [Agent Scanning Directory]: {}", path);
    let mut output = String::new();
    
    let walker = WalkBuilder::new(path)
        .max_depth(max_depth)
        .hidden(true) // Ignore .git, .env, etc.
        .build();

    for result in walker {
        match result {
            Ok(entry) => {
                let path_str = entry.path().display().to_string();
                if entry.file_type().map_or(false, |ft| ft.is_dir()) {
                    output.push_str(&format!("📁 {}\n", path_str));
                } else {
                    output.push_str(&format!("  📄 {}\n", path_str));
                }
            }
            Err(_) => continue,
        }
    }
    
    if output.is_empty() {
        "Directory is empty or not found.".to_string()
    } else {
        output
    }
}

/// A structured wrapper around Git to provide exact context
pub fn git_context(action: &str) -> String {
    println!("🌿 [Agent Inspecting Git]: {}", action);
    let arg = match action {
        "status" => "status --short",
        "diff" => "diff --no-ext-diff",
        "log" => "log --oneline -n 5",
        _ => return "Error: Invalid git action. Use 'status', 'diff', or 'log'.".to_string(),
    };

    let output = Command::new("git").arg(arg).output();
    match output {
        Ok(out) => {
            let stdout = String::from_utf8_lossy(&out.stdout).to_string();
            if stdout.trim().is_empty() {
                "No output (clean working tree or empty log).".to_string()
            } else {
                stdout
            }
        }
        Err(e) => format!("Git Error: {}", e),
    }
}
