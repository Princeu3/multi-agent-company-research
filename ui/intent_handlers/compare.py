"""
Compare Intent Handler

Handles the "compare" intent - comparing multiple companies.

Student Guide:
--------------
This handler:
1. Takes a list of companies to compare
2. Fetches their scores from database
3. Creates a comparison with rankings
4. Shows detailed category breakdowns
5. Adds insights about the comparison

The comparison shows:
- Winner (highest score)
- Detailed scores for each company
- Category breakdowns (Environmental, Social, Governance)
- Insights based on score differences
"""

import streamlit as st
from typing import List
from ui.components.sidebar import get_companies_from_db


def handle_compare(companies: List[str]):
    """
    Handle the compare intent - compare multiple companies.

    This function assumes all companies have already been analyzed
    (handled by the analyze step first).

    Args:
        companies: List of company names to compare

    Example:
        handle_compare(["Tesla", "Apple", "Microsoft"])
        # Compares all three companies and shows results in chat
    """
    if len(companies) < 2:
        response = "⚠️ I need at least 2 companies to compare."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    response = f"📊 **Comparison: {' vs '.join(companies)}**\n\n"

    # Fetch companies data from database
    companies_data = get_companies_from_db()
    comparison_data = []

    for company in companies:
        if company in companies_data:
            data = companies_data[company]
            comparison_data.append({
                'name': company,
                'score': data['scores']['final_score'],
                'env': data['scores']['environmental_score'],
                'social': data['scores']['social_score'],
                'gov': data['scores']['governance_score']
            })

    if len(comparison_data) >= 2:
        # Sort by score (highest first)
        comparison_data.sort(key=lambda x: x['score'], reverse=True)

        # Show winner
        winner = comparison_data[0]
        response += f"🏆 **Winner: {winner['name']}** with {winner['score']:.1f}/100\n\n"

        response += "**Detailed Comparison:**\n\n"
        for comp in comparison_data:
            response += f"**{comp['name']}**: {comp['score']:.1f}/100\n"
            response += f"- 🌍 Environmental: {comp['env']:.1f}\n"
            response += f"- 👥 Social: {comp['social']:.1f}\n"
            response += f"- ⚖️ Governance: {comp['gov']:.1f}\n\n"

        # Add insights based on score difference
        diff = comparison_data[0]['score'] - comparison_data[1]['score']
        if diff > 10:
            response += f"💡 {comparison_data[0]['name']} significantly outperforms with a {diff:.1f} point lead."
        elif diff > 5:
            response += f"💡 {comparison_data[0]['name']} has a moderate lead of {diff:.1f} points."
        else:
            response += f"💡 Very close! Only {diff:.1f} points separate them."

    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()
