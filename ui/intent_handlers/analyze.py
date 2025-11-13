"""
Analyze Intent Handler

Handles the "analyze" intent - analyzing new companies.

Student Guide:
--------------
This handler:
1. Takes a list of companies that need analysis
2. Analyzes each one (research → extract → score → save to DB)
3. Adds success/failure messages to chat
4. Clears cache to show new companies in sidebar

The actual analysis is done by:
- ResearchAgent (research/agent.py) - Web research
- MetricsExtractor (analysis/extractor.py) - Extract metrics with AI
- SustainabilityScorer (analysis/scorer.py) - Calculate scores
- DatabaseManager (database/db_manager.py) - Save to database
"""

import streamlit as st
from typing import List
from research.agent import ResearchAgent
from database.db_manager import DatabaseManager
from analysis.extractor import MetricsExtractor
from analysis.scorer import SustainabilityScorer
from ui.components.sidebar import get_companies_from_db, get_score_level
import os


def analyze_company_helper(company_name: str) -> dict:
    """
    Analyze a single company and save to database.

    This is the core analysis function that:
    1. Checks if company is already analyzed (cached)
    2. If not, performs full analysis pipeline
    3. Saves results to database
    4. Returns success status and score

    Args:
        company_name: Name of the company to analyze

    Returns:
        dict: {
            'success': bool,
            'score': float (if success),
            'level': str (if success),
            'cached': bool (if success)
        }

    Example:
        result = analyze_company_helper("Tesla")
        if result['success']:
            print(f"Tesla score: {result['score']}")
    """
    db = DatabaseManager()
    research_agent = ResearchAgent()
    extractor = MetricsExtractor()
    scorer = SustainabilityScorer()

    # Check cache first
    cache_days = int(os.getenv('CACHE_EXPIRY_DAYS', 7))
    cached = db.get_recent_analysis(company_name, days=cache_days)

    if cached:
        company_data, sources, metrics, scores = cached
        # Ensure score_level exists
        if 'score_level' not in scores:
            scores['score_level'] = get_score_level(scores['final_score'])
        return {
            'success': True,
            'score': scores['final_score'],
            'level': scores['score_level'],
            'cached': True
        }

    # Perform analysis
    research_result = research_agent.research_company(company_name)
    if not research_result['sources']:
        return {'success': False}

    company_id = db.save_research(company_name, research_result['sources'])
    metrics = extractor.extract_metrics(company_name, research_result['sources'])
    db.save_metrics(company_id, metrics)
    scores = scorer.calculate_final_score(metrics)
    db.save_scores(company_id, scores)

    # Clear cache to force reload from database
    get_companies_from_db.clear()

    # Ensure score_level exists
    if 'score_level' not in scores:
        scores['score_level'] = get_score_level(scores['final_score'])

    return {
        'success': True,
        'score': scores['final_score'],
        'level': scores['score_level'],
        'cached': False
    }


def handle_analyze(needs_analysis: List[str]):
    """
    Handle the analyze intent - analyze companies that need analysis.

    This function is called when the user wants to analyze one or more companies.
    It processes each company and adds messages to the chat.

    Args:
        needs_analysis: List of company names to analyze

    Example:
        handle_analyze(["Tesla", "Apple"])
        # Analyzes both companies and adds results to chat
    """
    if not needs_analysis:
        return

    response = f"Let me analyze {', '.join(needs_analysis)} first...\n\n"
    st.session_state.chat_messages.append({"role": "assistant", "content": response})

    for company in needs_analysis:
        with st.chat_message("assistant"):
            with st.spinner(f"🔍 Analyzing {company}..."):
                result = analyze_company_helper(company)

                if result['success']:
                    msg = f"✅ **{company}** analyzed! Score: {result['score']:.1f}/100 ({result['level']})"
                    st.session_state.chat_messages.append({"role": "assistant", "content": msg})
                else:
                    msg = f"❌ Couldn't find information about {company}"
                    st.session_state.chat_messages.append({"role": "assistant", "content": msg})

    st.rerun()
