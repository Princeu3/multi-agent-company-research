-- Company Sustainability Scoring System Database Schema

-- Companies table: stores basic company information
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    research_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research sources table: stores URLs and content from research
CREATE TABLE IF NOT EXISTS research_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    content TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Sustainability metrics table: stores extracted metrics from analysis
CREATE TABLE IF NOT EXISTS sustainability_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    category TEXT NOT NULL, -- Environmental, Social, Governance
    metric_name TEXT NOT NULL,
    value REAL, -- Score 0-100
    confidence REAL, -- Confidence score 0-1
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Sustainability scores table: stores final calculated scores
CREATE TABLE IF NOT EXISTS sustainability_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    final_score REAL NOT NULL, -- Overall score 0-100
    environmental_score REAL,
    social_score REAL,
    governance_score REAL,
    component_scores_json TEXT, -- JSON with detailed component breakdown
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_research_sources_company ON research_sources(company_id);
CREATE INDEX IF NOT EXISTS idx_metrics_company ON sustainability_metrics(company_id);
CREATE INDEX IF NOT EXISTS idx_metrics_category ON sustainability_metrics(category);
CREATE INDEX IF NOT EXISTS idx_scores_company ON sustainability_scores(company_id);
CREATE INDEX IF NOT EXISTS idx_companies_research_date ON companies(research_date);
