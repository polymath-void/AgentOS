pub struct HeuristicSummarizer;

impl HeuristicSummarizer {
    /// Extracts the most representative sentences based on simple heuristic (sentence length/position).
    pub fn summarize(text: &str, max_chars: usize) -> String {
        let sentences: Vec<&str> = text.split_inclusive(|c| c == '.' || c == '?' || c == '!').collect();
        let mut summary = String::new();

        for sentence in sentences {
            // Heuristic: Keep sentences that look substantive
            if sentence.len() > 20 {
                if summary.len() + sentence.len() > max_chars {
                    break;
                }
                summary.push_str(sentence);
                summary.push(' ');
            }
        }

        if summary.is_empty() {
            // Fallback to simple truncation
            text.chars().take(max_chars).collect()
        } else {
            summary.trim().to_string()
        }
    }
}
