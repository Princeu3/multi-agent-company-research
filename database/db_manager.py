"""
Database Manager for Company Sustainability Scoring System

This module handles ALL database operations using SQLite:
1. Saving research data, metrics, and scores
2. Retrieving company information
3. Checking for cached (recently analyzed) data
4. Managing the complete data lifecycle

Student Guide:
--------------
Database Structure (4 tables):
1. companies: Basic company info (name, dates)
2. research_sources: Scraped URLs and content
3. sustainability_metrics: Individual metric scores (15 per company)
4. sustainability_scores: Final calculated scores

Key Concepts:
- SQLite: File-based database (saved as .db file)
- CRUD: Create, Read, Update, Delete operations
- Foreign Keys: Links between tables (CASCADE delete)
- Caching: Reuse recent analysis (default: 7 days)

Main Functions:
- save_research(): Store scraped content
- save_metrics(): Store extracted metrics
- save_scores(): Store calculated scores
- get_recent_analysis(): Check for cached data
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all database operations for the sustainability scoring system.

    This class is responsible for:
    - Creating and initializing the database
    - Storing research, metrics, and scores
    - Retrieving data efficiently
    - Managing cache expiry

    Example usage:
        db = DatabaseManager()
        company_id = db.save_research("Tesla", sources)
        db.save_metrics(company_id, metrics)
        db.save_scores(company_id, scores)

        # Later, check for cached data
        cached = db.get_recent_analysis("Tesla", days=7)
        if cached:
            # Use cached data instead of reanalyzing
            company, sources, metrics, scores = cached
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the Database Manager.

        Args:
            db_path: Path to SQLite database file
                    If None, uses DATABASE_PATH from .env or defaults to 'sustainability_data.db'

        Example:
            db = DatabaseManager()  # Uses default path
            db = DatabaseManager("my_custom.db")  # Uses custom path
        """
        # Get database path from argument, env, or default
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'sustainability_data.db')

        # Create database and tables if they don't exist
        self._initialize_database()

        logger.info(f"✓ Database initialized at: {self.db_path}")

    def _initialize_database(self):
        """
        Create database schema if it doesn't exist.

        Reads the schema.sql file and executes it to create all tables,
        indexes, and relationships. This is safe to call multiple times -
        it only creates tables that don't exist yet (IF NOT EXISTS).
        """
        # Get path to schema.sql file (in same directory as this file)
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

        # Read the SQL schema
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        # Execute the schema to create tables
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()

        logger.info("Database schema initialized successfully")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with row factory enabled.

        Row factory allows us to access results as dictionaries instead
        of tuples, which is more convenient: row['name'] instead of row[0]

        Returns:
            SQLite connection object ready to use
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dictionary-like access
        conn.execute("PRAGMA foreign_keys = ON")  # CRITICAL: Enable foreign key constraints!
        return conn

    def save_research(self, company_name: str, sources: List[Dict[str, str]]) -> int:
        """
        Save research data (scraped sources) for a company.

        This function:
        1. Creates or updates the company record
        2. Deletes any old research sources for this company
        3. Saves all new research sources

        Args:
            company_name: Name of the company
            sources: List of dicts with 'url' and 'content' keys
                     Example: [{"url": "...", "content": "..."}]

        Returns:
            company_id: Database ID of the company record

        Example:
            sources = [
                {"url": "https://tesla.com/impact", "content": "Tesla's impact..."},
                {"url": "https://news.com/tesla", "content": "News about Tesla..."}
            ]
            company_id = db.save_research("Tesla", sources)
            # Returns: 1 (or whatever ID was assigned)
        """
        logger.info(f"💾 Saving research data for: {company_name}")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # STEP 1: Insert or update company record
            # ON CONFLICT: If company exists, update dates
            cursor.execute("""
                INSERT INTO companies (name, research_date, last_updated)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    research_date = excluded.research_date,
                    last_updated = excluded.last_updated
            """, (company_name, datetime.now(), datetime.now()))

            # STEP 2: Get the company ID
            cursor.execute("SELECT id FROM companies WHERE name = ?", (company_name,))
            company_id = cursor.fetchone()[0]

            # STEP 3: Delete old research sources (replace with new ones)
            cursor.execute("DELETE FROM research_sources WHERE company_id = ?", (company_id,))

            # STEP 4: Insert new research sources
            for source in sources:
                cursor.execute("""
                    INSERT INTO research_sources (company_id, url, content, scraped_at)
                    VALUES (?, ?, ?, ?)
                """, (company_id, source['url'], source['content'], datetime.now()))

            # Save changes to database
            conn.commit()

        logger.info(f"✅ Saved {len(sources)} research sources for company_id: {company_id}")
        return company_id

    def save_metrics(self, company_id: int, metrics: List[Dict]) -> None:
        """
        Save sustainability metrics for a company.

        Stores all 15 metrics (5 per category) in the database.
        Deletes any existing metrics for this company first to avoid duplicates.

        Args:
            company_id: ID of the company
            metrics: List of metric dictionaries with keys:
                    'category', 'metric_name', 'value', 'confidence'

        Example:
            metrics = [
                {"category": "Environmental", "metric_name": "Carbon", "value": 85, "confidence": 0.9},
                {"category": "Social", "metric_name": "Labor", "value": 70, "confidence": 0.8},
                ...
            ]
            db.save_metrics(company_id, metrics)
        """
        logger.info(f"💾 Saving {len(metrics)} metrics for company_id: {company_id}")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # STEP 1: Delete old metrics (replace with new ones)
            cursor.execute("DELETE FROM sustainability_metrics WHERE company_id = ?", (company_id,))

            # STEP 2: Insert new metrics
            for metric in metrics:
                cursor.execute("""
                    INSERT INTO sustainability_metrics
                    (company_id, category, metric_name, value, confidence, extracted_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    company_id,
                    metric['category'],
                    metric['metric_name'],
                    metric['value'],
                    metric['confidence'],
                    datetime.now()
                ))

            # Save changes
            conn.commit()

        logger.info(f"✅ Successfully saved metrics for company_id: {company_id}")

    def save_scores(self, company_id: int, scores: Dict) -> None:
        """
        Save sustainability scores for a company.

        Stores the final calculated scores including:
        - Final overall score
        - Individual category scores (Environmental, Social, Governance)
        - Component scores (detailed breakdown as JSON)

        Args:
            company_id: ID of the company
            scores: Dictionary with keys:
                   'final_score', 'environmental_score', 'social_score',
                   'governance_score', 'component_scores' (dict)

        Example:
            scores = {
                'final_score': 75.5,
                'environmental_score': 80.0,
                'social_score': 70.0,
                'governance_score': 77.0,
                'component_scores': {...}  # Detailed breakdown
            }
            db.save_scores(company_id, scores)
        """
        logger.info(f"💾 Saving scores for company_id: {company_id}")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Convert component scores dictionary to JSON string for storage
            component_scores_json = json.dumps(scores.get('component_scores', {}))

            # Insert new score record
            cursor.execute("""
                INSERT INTO sustainability_scores
                (company_id, final_score, environmental_score, social_score,
                 governance_score, component_scores_json, calculated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                scores['final_score'],
                scores.get('environmental_score'),
                scores.get('social_score'),
                scores.get('governance_score'),
                component_scores_json,
                datetime.now()
            ))

            # Save changes
            conn.commit()

        logger.info(f"✅ Successfully saved scores for company_id: {company_id}")

    def get_company(self, company_name: str) -> Optional[Dict]:
        """
        Get company information by name.

        Args:
            company_name: Name of the company to find

        Returns:
            Dictionary with company data (id, name, dates) or None if not found

        Example:
            company = db.get_company("Tesla")
            if company:
                print(f"Found: {company['name']}, ID: {company['id']}")
            else:
                print("Company not found")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM companies WHERE name = ?", (company_name,))
            row = cursor.fetchone()

            if row:
                return dict(row)  # Convert to dictionary
            return None

    def get_research_sources(self, company_id: int) -> List[Dict]:
        """
        Get all research sources for a company.

        Args:
            company_id: ID of the company

        Returns:
            List of source dictionaries (url, content, scraped_at, etc.)

        Example:
            sources = db.get_research_sources(company_id)
            for source in sources:
                print(f"URL: {source['url']}")
                print(f"Content length: {len(source['content'])} chars")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM research_sources
                WHERE company_id = ?
                ORDER BY scraped_at DESC
            """, (company_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_metrics(self, company_id: int) -> List[Dict]:
        """
        Get all sustainability metrics for a company.

        Args:
            company_id: ID of the company

        Returns:
            List of 15 metric dictionaries (category, metric_name, value, confidence)

        Example:
            metrics = db.get_metrics(company_id)
            for metric in metrics:
                print(f"{metric['category']}: {metric['metric_name']} = {metric['value']}")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sustainability_metrics
                WHERE company_id = ?
                ORDER BY category, metric_name
            """, (company_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_latest_score(self, company_id: int) -> Optional[Dict]:
        """
        Get the most recent sustainability score for a company.

        Args:
            company_id: ID of the company

        Returns:
            Score dictionary with all scores and component breakdown, or None if not found

        Example:
            scores = db.get_latest_score(company_id)
            if scores:
                print(f"Final Score: {scores['final_score']}/100")
                print(f"Components: {scores['component_scores']}")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sustainability_scores
                WHERE company_id = ?
                ORDER BY calculated_at DESC
                LIMIT 1
            """, (company_id,))

            row = cursor.fetchone()
            if row:
                score_dict = dict(row)
                # Parse JSON component scores back to dictionary
                if score_dict.get('component_scores_json'):
                    score_dict['component_scores'] = json.loads(score_dict['component_scores_json'])
                return score_dict
            return None

    def get_recent_analysis(self, company_name: str, days: int = 7) -> Optional[Tuple[Dict, List[Dict], List[Dict], Dict]]:
        """
        Get recent analysis for a company if it exists within the cache period.

        This is a CACHE CHECK function. It returns existing data only if:
        1. Company has been analyzed before
        2. Analysis is recent (within 'days' parameter)
        3. All required data exists (sources and scores)

        If any condition fails, returns None (meaning: reanalyze the company).

        Args:
            company_name: Name of the company
            days: Number of days to consider as "recent" (default: 7)

        Returns:
            Tuple of (company, sources, metrics, scores) if recent analysis exists
            None if no recent analysis (need to analyze again)

        Example:
            # Check if we have recent data (within 7 days)
            cached = db.get_recent_analysis("Tesla", days=7)

            if cached:
                # Use cached data
                company, sources, metrics, scores = cached
                print(f"Using cached data from {company['research_date']}")
            else:
                # Need to analyze again
                print("No recent data, running new analysis...")
        """
        # Get company record
        company = self.get_company(company_name)

        if not company:
            # Company not in database yet
            return None

        # Check if analysis is recent enough
        research_date = datetime.fromisoformat(company['research_date'])
        cache_expiry = datetime.now() - timedelta(days=days)

        if research_date < cache_expiry:
            # Analysis is too old
            logger.info(f"⏰ Analysis for {company_name} is older than {days} days")
            return None

        # Get all associated data
        sources = self.get_research_sources(company['id'])
        metrics = self.get_metrics(company['id'])
        scores = self.get_latest_score(company['id'])

        # Make sure we have all required data
        if not sources or not scores:
            logger.info(f"⚠️ Incomplete analysis data for {company_name}")
            return None

        logger.info(f"✅ Found recent analysis for {company_name} from {research_date}")
        return (company, sources, metrics, scores)

    def get_all_companies(self) -> List[Dict]:
        """
        Get all companies in the database.

        Returns:
            List of company dictionaries, ordered by most recent first

        Example:
            companies = db.get_all_companies()
            for company in companies:
                print(f"- {company['name']} (analyzed: {company['research_date']})")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM companies
                ORDER BY research_date DESC
            """)

            return [dict(row) for row in cursor.fetchall()]


def test_database_manager():
    """
    Test the Database Manager with sample data.

    This test:
    1. Creates a test database
    2. Saves sample research, metrics, and scores
    3. Retrieves the data back
    4. Tests the caching functionality
    5. Cleans up the test database
    """
    print("=" * 70)
    print("TESTING DATABASE MANAGER")
    print("=" * 70)

    try:
        # STEP 1: Initialize test database
        db = DatabaseManager("test_sustainability.db")
        print("✓ Database initialized\n")

        # STEP 2: Prepare test data
        company_name = "Tesla"
        test_sources = [
            {
                "url": "https://example.com/tesla-sustainability",
                "content": "Tesla is committed to sustainability and reducing carbon emissions..."
            },
            {
                "url": "https://example.com/tesla-emissions",
                "content": "Tesla's carbon emissions data shows significant improvement..."
            }
        ]

        # STEP 3: Save research
        print("Saving research data...")
        company_id = db.save_research(company_name, test_sources)
        print(f"✓ Saved research (company_id: {company_id})\n")

        # STEP 4: Save metrics
        print("Saving metrics...")
        test_metrics = [
            {
                "category": "Environmental",
                "metric_name": "Carbon Emissions",
                "value": 85.0,
                "confidence": 0.9
            },
            {
                "category": "Social",
                "metric_name": "Labor Practices",
                "value": 70.0,
                "confidence": 0.8
            },
            {
                "category": "Governance",
                "metric_name": "Board Independence",
                "value": 75.0,
                "confidence": 0.85
            }
        ]
        db.save_metrics(company_id, test_metrics)
        print(f"✓ Saved {len(test_metrics)} metrics\n")

        # STEP 5: Save scores
        print("Saving scores...")
        test_scores = {
            "final_score": 78.5,
            "environmental_score": 85.0,
            "social_score": 70.0,
            "governance_score": 75.0,
            "component_scores": {
                "environmental_overall": 85,
                "social_overall": 70,
                "governance_overall": 75
            }
        }
        db.save_scores(company_id, test_scores)
        print("✓ Saved scores\n")

        # STEP 6: Retrieve data
        print("=" * 70)
        print("RETRIEVING DATA")
        print("=" * 70)

        company = db.get_company(company_name)
        print(f"✓ Retrieved company: {company['name']}")

        sources = db.get_research_sources(company_id)
        print(f"✓ Retrieved {len(sources)} sources")

        metrics = db.get_metrics(company_id)
        print(f"✓ Retrieved {len(metrics)} metrics")

        scores = db.get_latest_score(company_id)
        print(f"✓ Retrieved scores: {scores['final_score']}/100\n")

        # STEP 7: Test caching
        print("=" * 70)
        print("TESTING CACHE")
        print("=" * 70)

        cached = db.get_recent_analysis(company_name, days=7)
        if cached:
            print(f"✓ Found cached analysis for {company_name}")
            print(f"  Research date: {cached[0]['research_date']}")
            print(f"  Sources: {len(cached[1])}")
            print(f"  Metrics: {len(cached[2])}")
            print(f"  Final score: {cached[3]['final_score']}")
        else:
            print("✗ No cached analysis found")

        print("\n" + "=" * 70)
        print("✅ TEST PASSED: All database operations successful")
        print("=" * 70)

        # STEP 8: Cleanup
        import os
        if os.path.exists("test_sustainability.db"):
            os.remove("test_sustainability.db")
            print("✓ Cleaned up test database")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


# When this file is run directly, run the test
if __name__ == "__main__":
    test_database_manager()
