"""
Sidebar Component

This module handles the sidebar display showing analyzed companies.

Student Guide:
--------------
The sidebar shows:
- List of all analyzed companies from database
- Each company's score and level
- Delete buttons for each company
- Clear all button
- About information

Why separate the sidebar?
- Keeps app.py clean and focused
- Sidebar logic is self-contained
- Easy to test independently
- Can reuse in other pages if needed
"""

import streamlit as st
import os
from database.db_manager import DatabaseManager


def get_score_level(score: float) -> str:
    """
    Calculate score level from numerical score.

    Args:
        score: Numerical score (0-100)

    Returns:
        str: Score level (Excellent, Good, Fair, Poor, Very Poor)

    Example:
        level = get_score_level(85)  # Returns "Excellent"
        level = get_score_level(55)  # Returns "Fair"
    """
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    elif score >= 30:
        return "Poor"
    else:
        return "Very Poor"


@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_companies_from_db():
    """
    Fetch all recent companies from database with caching.

    This function:
    1. Gets all companies from database
    2. Fetches their recent analysis data (within cache period)
    3. Returns a dictionary of company data

    Why cache?
    - Avoid excessive database queries
    - 10-second TTL ensures data is reasonably fresh
    - Improves app performance

    Returns:
        dict: Dictionary mapping company names to their data
              {
                  "Tesla": {
                      "company": {...},
                      "sources": [...],
                      "metrics": [...],
                      "scores": {...}
                  },
                  ...
              }

    Example:
        companies_data = get_companies_from_db()
        if "Tesla" in companies_data:
            print(f"Score: {companies_data['Tesla']['scores']['final_score']}")
    """
    try:
        db = DatabaseManager()
        all_companies = db.get_all_companies()

        companies_data = {}
        cache_days = int(os.getenv('CACHE_EXPIRY_DAYS', 7))

        for company in all_companies:
            cached = db.get_recent_analysis(company['name'], days=cache_days)
            if cached:
                company_data, sources, metrics, scores = cached

                # Ensure score_level exists
                if 'score_level' not in scores:
                    scores['score_level'] = get_score_level(scores['final_score'])

                companies_data[company['name']] = {
                    'company': company_data,
                    'sources': sources,
                    'metrics': metrics,
                    'scores': scores
                }

        return companies_data
    except Exception as e:
        st.error(f"Error fetching companies: {str(e)}")
        return {}


def render_sidebar():
    """
    Render the complete sidebar with company list and controls.

    This function handles:
    1. Displaying analyzed companies with scores
    2. Delete buttons for each company
    3. Clear all button
    4. About information
    5. Score interpretation guide

    Example:
        from ui.components.sidebar import render_sidebar

        with st.sidebar:
            render_sidebar()
    """
    st.header("📋 Analyzed Companies")

    # Fetch companies from database
    companies_data = get_companies_from_db()

    if companies_data:
        # Display each company with delete button
        companies_to_delete = []
        for company_name, data in companies_data.items():
            if data:
                score = data['scores']['final_score']
                level = data['scores']['score_level']

                # Choose color indicator based on score
                color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"

                # Create columns for company info and delete button
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{color} **{company_name}**  \n{score:.1f} ({level})")
                with col2:
                    if st.button("🗑️", key=f"delete_{company_name}", help=f"Delete {company_name}"):
                        companies_to_delete.append(company_name)

        # Delete companies from database
        if companies_to_delete:
            db = DatabaseManager()
            for company in companies_to_delete:
                # Delete from database (CASCADE will delete related records)
                with db._get_connection() as conn:
                    conn.execute("DELETE FROM companies WHERE name = ?", (company,))
                    conn.commit()

            # Clear cache and add notification
            get_companies_from_db.clear()
            deleted_msg = f"🗑️ Deleted from database: {', '.join(companies_to_delete)}"
            if 'chat_messages' in st.session_state:
                st.session_state.chat_messages.append({"role": "assistant", "content": deleted_msg})
            st.rerun()

        st.divider()
        if st.button("🗑️ Clear All Companies", use_container_width=True):
            # Delete all companies from database
            db = DatabaseManager()
            with db._get_connection() as conn:
                conn.execute("DELETE FROM companies")
                conn.commit()

            # Clear cache
            get_companies_from_db.clear()
            if 'chat_messages' in st.session_state:
                st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.rerun()
    else:
        st.info("No companies analyzed yet")

    st.divider()

    # About section
    st.header("About")
    st.markdown("""
    This system analyzes company sustainability using:
    - **Perplexity AI** for research
    - **Firecrawl** for web scraping
    - **GPT-4o-mini** for analysis

    **Scoring Weights:**
    - Environmental: 40%
    - Social: 35%
    - Governance: 25%
    """)

    # Score interpretation guide
    st.header("Score Interpretation")
    st.markdown("""
    - **85-100**: Excellent
    - **70-84**: Good
    - **50-69**: Fair
    - **30-49**: Poor
    - **0-29**: Very Poor
    """)
