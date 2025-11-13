"""
History View Component

This module displays the analysis history table.

Student Guide:
--------------
The history view shows:
- All companies that have been analyzed
- Their scores and levels
- Date of analysis

Why separate the history view?
- Keeps history display logic separate
- Easy to modify table format
- Can be reused in reports or exports
- Clean separation of concerns
"""

import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager


def render_history_view():
    """
    Render the analysis history table.

    This function:
    1. Fetches all companies from database
    2. Gets their latest scores
    3. Displays them in a table format

    Example:
        from ui.components.history_view import render_history_view

        with st.tabs(["Chat", "History"])[1]:
            render_history_view()
    """
    st.header("Analysis History")

    db = DatabaseManager()
    companies = db.get_all_companies()

    if companies:
        st.markdown(f"**{len(companies)} companies analyzed:**")

        history_data = []
        for company in companies:
            score = db.get_latest_score(company['id'])
            if score:
                history_data.append({
                    'Company': company['name'],
                    'Score': f"{score['final_score']:.1f}",
                    'Level': score.get('score_level', 'N/A'),
                    'Date': company['research_date']
                })

        if history_data:
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No completed analyses found")
    else:
        st.info("No companies analyzed yet. Start by analyzing a company in the Chat tab!")
