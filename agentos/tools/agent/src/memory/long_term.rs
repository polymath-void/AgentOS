use rusqlite::{params, Connection, Result};
use std::sync::Mutex;

pub struct LongTermMemory {
    conn: Mutex<Connection>,
}

impl LongTermMemory {
    /// Initializes SQLite database and sets up system tables.
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        
        // Existing facts table
        conn.execute(
            "CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key_name TEXT NOT NULL UNIQUE,
                fact_value TEXT NOT NULL
            )",
            [],
        )?;

        // New skills table for adaptive methodologies
        conn.execute(
            "CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL UNIQUE,
                context_trigger TEXT NOT NULL,
                methodology TEXT NOT NULL
            )",
            [],
        )?;

        Ok(Self { conn: Mutex::new(conn) })
    }

    /// Store or update a key project fact.
    #[allow(dead_code)]
    pub fn set_fact(&self, category: &str, key: &str, value: &str) -> Result<()> {
        self.conn.lock().unwrap().execute(
            "INSERT INTO facts (category, key_name, fact_value)
             VALUES (?1, ?2, ?3)
             ON CONFLICT(key_name) DO UPDATE SET fact_value=excluded.fact_value",
            params![category, key, value],
        )?;
        Ok(())
    }

    /// Retrieve all persistent facts formatted for System Instruction injection.
    pub fn get_formatted_facts(&self) -> Result<String> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare("SELECT category, key_name, fact_value FROM facts")?;
        let fact_rows = stmt.query_map([], |row| {
            let category: String = row.get(0)?;
            let key: String = row.get(1)?;
            let val: String = row.get(2)?;
            Ok(format!("[{}] {}: {}", category, key, val))
        })?;

        let mut facts = Vec::new();
        for fact in fact_rows {
            facts.push(fact?);
        }

        if facts.is_empty() {
            Ok("No stored persistent memory facts available.".to_string())
        } else {
            Ok(facts.join("\n"))
        }
    }

    /// Agent calls this to permanently memorize a successful workflow
    pub fn learn_skill(&self, name: &str, trigger: &str, methodology: &str) -> Result<()> {
        self.conn.lock().unwrap().execute(
            "INSERT INTO skills (skill_name, context_trigger, methodology)
             VALUES (?1, ?2, ?3)
             ON CONFLICT(skill_name) DO UPDATE SET 
                context_trigger=excluded.context_trigger,
                methodology=excluded.methodology",
            params![name, trigger, methodology],
        )?;
        Ok(())
    }

    /// Retrieve all learned skills to inject into the active context
    pub fn get_learned_skills(&self) -> Result<String> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare("SELECT skill_name, methodology FROM skills")?;
        let skill_rows = stmt.query_map([], |row| {
            let name: String = row.get(0)?;
            let method: String = row.get(1)?;
            Ok(format!("- [{}]: {}", name, method))
        })?;

        let mut skills = Vec::new();
        for fact in skill_rows {
            skills.push(fact?);
        }

        if skills.is_empty() {
            Ok("No specialized skills adapted yet.".to_string())
        } else {
            Ok(skills.join("\n"))
        }
    }
}
