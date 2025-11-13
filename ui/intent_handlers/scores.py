"""
Score Display Intent Handlers

Handles score-related intents:
- show_score: Show overall score
- show_details: Show detailed analysis
- show_environmental/social/governance: Show category-specific info
- show_strengths_weaknesses: Show top/bottom metrics

Student Guide:
--------------
These handlers fetch company data from the database and
format it nicely for display in the chat.

Each handler focuses on one type of information:
- Overall scores
- Category breakdowns
- Detailed metrics
- Strengths and weaknesses
"""

import streamlit as st
from typing import List
from ui.components.sidebar import get_companies_from_db


def handle_show_score(companies: List[str]):
    """
    Handle show_score intent - display overall score.

    Args:
        companies: List of company names (usually just one)

    Example:
        handle_show_score(["Tesla"])
        # Shows: "Tesla's Sustainability Score: 63.5/100 (Fair)"
    """
    company_name = companies[0] if companies else None
    if not company_name:
        response = "Please specify a company to check the score."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    companies_data = get_companies_from_db()
    if company_name in companies_data:
        data = companies_data[company_name]
        scores = data['scores']
        response = f"**{company_name}'s Sustainability Score:**\n\n"
        response += f"🎯 **Overall: {scores['final_score']:.1f}/100** ({scores['score_level']})\n\n"
        response += f"That's based on:\n"
        response += f"- 🌍 Environmental: {scores['environmental_score']:.1f}/100\n"
        response += f"- 👥 Social: {scores['social_score']:.1f}/100\n"
        response += f"- ⚖️ Governance: {scores['governance_score']:.1f}/100"
    else:
        response = f"I haven't analyzed {company_name} yet."

    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()


def handle_show_details(companies: List[str]):
    """
    Handle show_details intent - display detailed analysis.

    Args:
        companies: List of company names (usually just one)

    Example:
        handle_show_details(["Tesla"])
        # Shows full breakdown with top strengths and areas for improvement
    """
    company_name = companies[0] if companies else None
    if not company_name:
        response = "Please specify a company."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    companies_data = get_companies_from_db()
    if company_name in companies_data:
        data = companies_data[company_name]
        scores = data['scores']

        response = f"📊 **Detailed Analysis for {company_name}**\n\n"
        response += f"**Overall Score:** {scores['final_score']:.1f}/100 ({scores['score_level']})\n\n"
        response += f"**Category Breakdown:**\n"
        response += f"- 🌍 Environmental: {scores['environmental_score']:.1f}/100 (40% weight)\n"
        response += f"- 👥 Social: {scores['social_score']:.1f}/100 (35% weight)\n"
        response += f"- ⚖️ Governance: {scores['governance_score']:.1f}/100 (25% weight)\n\n"

        # Get top 3 and bottom 3 metrics
        metrics = data['metrics']
        top_metrics = sorted(metrics, key=lambda x: x['value'], reverse=True)[:3]
        bottom_metrics = sorted(metrics, key=lambda x: x['value'])[:3]

        response += "**Strengths:**\n"
        for m in top_metrics:
            response += f"- {m['metric_name']}: {m['value']:.1f}/100\n"

        response += "\n**Areas for Improvement:**\n"
        for m in bottom_metrics:
            response += f"- {m['metric_name']}: {m['value']:.1f}/100\n"
    else:
        response = f"I haven't analyzed {company_name} yet."

    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()


def handle_show_category(companies: List[str], intent: str):
    """
    Handle category-specific intents (environmental, social, governance).

    Args:
        companies: List of company names (usually just one)
        intent: The specific intent (show_environmental, show_social, show_governance)

    Example:
        handle_show_category(["Tesla"], "show_environmental")
        # Shows Tesla's environmental metrics and score
    """
    company_name = companies[0] if companies else None
    if not company_name:
        response = "Please specify a company."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    companies_data = get_companies_from_db()
    if company_name in companies_data:
        data = companies_data[company_name]
        metrics = data['metrics']
        scores = data['scores']

        category_map = {
            "show_environmental": ("Environmental", "environmental_score", "🌍"),
            "show_social": ("Social", "social_score", "👥"),
            "show_governance": ("Governance", "governance_score", "⚖️")
        }

        category, score_key, emoji = category_map[intent]
        category_metrics = [m for m in metrics if m['category'] == category]

        response = f"{emoji} **{company_name}'s {category} Performance:**\n\n"
        response += f"**Score: {scores[score_key]:.1f}/100**\n\n"
        response += f"**Key Metrics:**\n"
        for m in sorted(category_metrics, key=lambda x: x['value'], reverse=True):
            icon = "✅" if m['value'] >= 75 else "⚠️" if m['value'] >= 50 else "❌"
            response += f"{icon} {m['metric_name']}: {m['value']:.1f}/100\n"
    else:
        response = f"I haven't analyzed {company_name} yet."

    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()


def handle_show_strengths_weaknesses(companies: List[str]):
    """
    Handle show_strengths_weaknesses intent - show top and bottom metrics.

    Args:
        companies: List of company names (usually just one)

    Example:
        handle_show_strengths_weaknesses(["Tesla"])
        # Shows top 5 strengths and bottom 5 weaknesses
    """
    company_name = companies[0] if companies else None
    if not company_name:
        response = "Please specify a company."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    companies_data = get_companies_from_db()
    if company_name in companies_data:
        data = companies_data[company_name]
        metrics = data['metrics']

        top_metrics = sorted(metrics, key=lambda x: x['value'], reverse=True)[:5]
        bottom_metrics = sorted(metrics, key=lambda x: x['value'])[:5]

        response = f"**{company_name}'s Strengths & Weaknesses:**\n\n"
        response += "💪 **Top Strengths:**\n"
        for m in top_metrics:
            response += f"- {m['metric_name']}: {m['value']:.1f}/100\n"

        response += "\n⚠️ **Areas Needing Improvement:**\n"
        for m in bottom_metrics:
            response += f"- {m['metric_name']}: {m['value']:.1f}/100\n"
    else:
        response = f"I haven't analyzed {company_name} yet."

    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()
