use serde_json::Value;

pub struct ShortTermMemory {
    history: Vec<Value>,
    max_turns: usize,
}

impl ShortTermMemory {
    pub fn new(max_turns: usize) -> Self {
        Self {
            history: Vec::new(),
            max_turns,
        }
    }

    /// Push a turn object (user, model, or function response) into the history.
    pub fn add_turn(&mut self, content_node: Value) {
        self.history.push(content_node);
        self.prune_if_needed();
    }

    /// Return the slice of messages formatted for Gemini API payload.
    pub fn get_contents(&self) -> Vec<Value> {
        self.history.clone()
    }

    pub fn get_recent_turns_as_string(&self, count: usize) -> String {
        self.history.iter().rev().take(count).rev()
            .map(|node| node["parts"][0]["text"].as_str().unwrap_or("").to_string())
            .collect::<Vec<_>>()
            .join("\n")
    }

    /// Trims oldest turns to prevent token expansion beyond model safety limits.
    fn prune_if_needed(&mut self) {
        if self.history.len() > self.max_turns {
            // Keep the initial setup turn and trim middle elements
            let overflow = self.history.len() - self.max_turns;
            self.history.drain(0..overflow);
        }
    }

    #[allow(dead_code)]
    pub fn clear(&mut self) {
        self.history.clear();
    }
}
