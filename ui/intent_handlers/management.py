"""
Management Intent Handlers

Handles management intents:
- delete: Delete specific companies
- clear: Clear all companies
- list_companies: List all analyzed companies

Student Guide:
--------------
These handlers manage the company data in the database:
- Delete removes specific companies
- Clear removes all companies
- List shows all analyzed companies

All operations work directly with the database and
clear the cache to ensure UI updates immediately.
"""

import streamlit as st
from typing import List
from database.db_manager import DatabaseManager
from ui.components.sidebar import get_companies_from_db


def handle_delete(companies: List[str]):
    """
    Handle delete intent - delete specific companies from database.

    Args:
        companies: List of company names to delete

    Example:
        handle_delete(["Tesla", "Apple"])
        # Deletes both Tesla and Apple from database
    """
    if not companies:
        response = "Please specify which company/companies to delete."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    deleted = []
    not_found = []

    db = DatabaseManager()
    companies_data = get_companies_from_db()

    for company in companies:
        if company in companies_data:
            # Delete from database (CASCADE will delete related records)
            with db._get_connection() as conn:
                conn.execute("DELETE FROM companies WHERE name = ?", (company,))
                conn.commit()
            deleted.append(company)
        else:
            not_found.append(company)

    # Clear cache after deletions
    if deleted:
        get_companies_from_db.clear()

    response = ""
    if deleted:
        response += f"🗑️ Deleted: {', '.join(deleted)}\n"
    if not_found:
        response += f"⚠️ Not found: {', '.join(not_found)}"

    st.session_state.chat_messages.append({"role": "assistant", "content": response.strip()})
    st.rerun()


def handle_clear():
    """
    Handle clear intent - delete all companies from database.

    Example:
        handle_clear()
        # Deletes all companies and resets chat
    """
    # Delete all companies from database
    db = DatabaseManager()
    with db._get_connection() as conn:
        conn.execute("DELETE FROM companies")
        conn.commit()

    # Clear cache
    get_companies_from_db.clear()

    # Reset chat to initial message
    if 'chat_messages' in st.session_state:
        st.session_state.chat_messages = [st.session_state.chat_messages[0]]

    st.rerun()


def handle_list_companies():
    """
    Handle list_companies intent - list all analyzed companies.

    Example:
        handle_list_companies()
        # Shows list of all companies with their scores
    """
    companies_data = get_companies_from_db()

    if companies_data:
        response = f"📋 **I've analyzed {len(companies_data)} companies:**\n\n"
        for name, data in companies_data.items():
            if data:
                score = data['scores']['final_score']
                response += f"- **{name}**: {score:.1f}/100\n"
    else:
        response = "I haven't analyzed any companies yet. Tell me a company name to get started!"

    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()
