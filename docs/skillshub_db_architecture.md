# SkillsHub DB Architecture

## Overview
SkillsHub DB is a specialized SQLite-based database designed for the ComputeRes OS. It enables agents to dynamically publish, discover, and share skills. It supports niche categorization, tagging, and robust search capabilities, including Full-Text Search (FTS5) and vector embeddings (sqlite-vss) for semantic discovery.

## Database Schema

### 1. `skills`
The core table storing skill metadata and location.
```sql
CREATE TABLE skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    author TEXT,
    version TEXT DEFAULT '1.0.0',
    code_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. `categories`
Stores niches or high-level domains for skills (e.g., "Web Scraping", "Data Analysis").
```sql
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);
```

### 3. `skill_categories`
Maps skills to their categories (many-to-many relationship).
```sql
CREATE TABLE skill_categories (
    skill_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (skill_id, category_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);
```

### 4. `tags`
Stores fine-grained tags for skills.
```sql
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
```

### 5. `skill_tags`
Maps skills to tags (many-to-many relationship).
```sql
CREATE TABLE skill_tags (
    skill_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (skill_id, tag_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);
```

### 6. `skills_fts` (FTS5 Virtual Table)
Enables ultra-fast keyword-based search over skills.
```sql
CREATE VIRTUAL TABLE skills_fts USING fts5(
    name,
    description,
    content='skills',
    content_rowid='skill_id'
);

-- Triggers to keep FTS table in sync with `skills`
CREATE TRIGGER skills_ai AFTER INSERT ON skills BEGIN
  INSERT INTO skills_fts(rowid, name, description) VALUES (new.skill_id, new.name, new.description);
END;

CREATE TRIGGER skills_ad AFTER DELETE ON skills BEGIN
  INSERT INTO skills_fts(skills_fts, rowid, name, description) VALUES('delete', old.skill_id, old.name, old.description);
END;

CREATE TRIGGER skills_au AFTER UPDATE ON skills BEGIN
  INSERT INTO skills_fts(skills_fts, rowid, name, description) VALUES('delete', old.skill_id, old.name, old.description);
  INSERT INTO skills_fts(rowid, name, description) VALUES (new.skill_id, new.name, new.description);
END;
```

### 7. `skills_embeddings` (sqlite-vss)
Utilizes vector embeddings for semantic search, finding skills by meaning rather than just exact keywords.
```sql
CREATE VIRTUAL TABLE skills_embeddings USING vss0(
    embedding(384) -- Assuming a 384-dimensional embedding model like all-MiniLM-L6-v2
);
```

---

## Operations & Methods

### Publishing (Insertion Methods)
When an agent creates a new skill, it is published to the SkillsHub via a Python API wrapper.

**`publish_skill(name: str, description: str, author: str, version: str, code_path: str, categories: list[str], tags: list[str], embedding: list[float] = None)`**
1. Inserts the base record into `skills` and retrieves the new `skill_id`.
2. Looks up or creates entries in `categories` and `tags`.
3. Creates associations in `skill_categories` and `skill_tags`.
4. If `embedding` is provided, inserts the generated vector into `skills_embeddings` using the `skill_id` as the rowid.
5. *(Note: The `skills_fts` table is automatically updated via SQLite triggers.)*

### Discovery (Querying Methods)
Agents can discover skills dynamically based on task requirements using multiple search strategies.

**1. Keyword Search (`search_skills_fts(query: str)`)**
Uses FTS5 to find skills by exact word matches, prefixes, or logical operators (AND/OR).
```sql
SELECT skills.*
FROM skills_fts
JOIN skills ON skills_fts.rowid = skills.skill_id
WHERE skills_fts MATCH ?
ORDER BY rank;
```

**2. Semantic Search (`search_skills_semantic(query_embedding: list[float], limit: int = 5)`)**
Finds conceptually related skills even if exact keywords don't match (requires embedding generation for the query text).
```sql
SELECT skills.*, distance
FROM skills_embeddings
JOIN skills ON skills.skill_id = skills_embeddings.rowid
WHERE vss_search(embedding, ?)
LIMIT ?;
```

**3. Filter by Category/Niche (`get_skills_by_niche(category_name: str)`)**
Returns all skills associated with a specific domain.
```sql
SELECT s.*
FROM skills s
JOIN skill_categories sc ON s.skill_id = sc.skill_id
JOIN categories c ON sc.category_id = c.category_id
WHERE c.name = ?;
```

**4. Hybrid Search (`discover_optimal_skill(query: str, query_embedding: list[float] = None, tags: list[str] = None)`)**
A combination method that could use FTS5 for initial broad filtering, optionally filtered down by specific tags, and ranked using semantic search distances.
