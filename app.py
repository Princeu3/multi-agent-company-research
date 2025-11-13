"""
Company Sustainability Scoring System
Main Streamlit Application

REFACTORED: Clean modular architecture!

Student Guide:
--------------
This file is now VERY simple because we've separated everything into modules:

1. ui/config.py - Page configuration and CSS
2. ui/components/sidebar.py - Sidebar display
3. ui/components/chat_interface.py - Chat UI helpers
4. ui/components/history_view.py - History table
5. ui/intent_handlers/ - All chat intent handlers

This makes the code:
- Easy to understand (each file has one job)
- Easy to test (test each module independently)
- Easy to maintain (find code quickly)
- Easy to extend (add new handlers/components easily)

The main app.py now just:
1. Sets up the page
2. Renders the sidebar
3. Creates tabs
4. Handles chat routing to intent handlers
"""

import streamlit as st

# Import UI modules
from ui.config import setup_page_config, apply_custom_css, get_initial_chat_message
from ui.components import (
    render_sidebar,
    initialize_chat_state,
    display_chat_messages,
    classify_user_intent,
    add_user_message,
    render_history_view
)
from ui.intent_handlers import (
    handle_analyze,
    handle_compare,
    handle_rag_question,
    handle_show_score,
    handle_show_details,
    handle_show_category,
    handle_show_strengths_weaknesses,
    handle_delete,
    handle_clear,
    handle_list_companies,
    handle_download
)


def main():
    """
    Main application entry point.

    This function:
    1. Sets up the page configuration
    2. Applies custom CSS
    3. Renders the sidebar
    4. Creates tabs for Chat and History
    5. Handles chat interaction and intent routing
    """
    # Setup page
    setup_page_config()
    apply_custom_css()

    # Header
    st.title("🌱 Company Sustainability Scoring System")
    st.markdown("Analyze companies' Environmental, Social, and Governance (ESG) practices using AI")

    # Initialize chat state
    initialize_chat_state(get_initial_chat_message())

    # Render sidebar
    with st.sidebar:
        render_sidebar()

    # Main content tabs
    tab1, tab2 = st.tabs(["💬 Chat Analysis", "📊 View History"])

    # TAB 1: Chat Analysis
    with tab1:
        st.header("💬 Chat Analysis Interface")
        st.markdown("Analyze multiple companies through a conversational interface")

        # Display chat messages
        display_chat_messages()

        # Chat input
        if prompt := st.chat_input("Ask me anything about companies' sustainability..."):
            # Add user message
            add_user_message(prompt)

            # Classify intent using LLM
            with st.spinner("🤔 Understanding your request..."):
                intent_data = classify_user_intent(prompt)

            # Extract intent components
            intent = intent_data.get('intent')
            companies = intent_data.get('companies', [])
            needs_analysis = intent_data.get('needs_analysis', [])
            question = intent_data.get('question')

            # STEP 1: Analyze companies that need analysis first
            if needs_analysis:
                handle_analyze(needs_analysis)

            # STEP 2: Route to appropriate intent handler
            # Management intents
            if intent == "clear":
                handle_clear()
            elif intent == "delete":
                handle_delete(companies)
            elif intent == "list_companies":
                handle_list_companies()

            # Comparison intent
            elif intent == "compare":
                handle_compare(companies)

            # Score display intents
            elif intent == "show_score":
                handle_show_score(companies)
            elif intent == "show_details":
                handle_show_details(companies)
            elif intent in ["show_environmental", "show_social", "show_governance"]:
                handle_show_category(companies, intent)
            elif intent == "show_strengths_weaknesses":
                handle_show_strengths_weaknesses(companies)

            # RAG question intent
            elif intent == "rag_question":
                handle_rag_question(companies, question)

            # Download intent
            elif intent == "download":
                handle_download(companies)

            # Analyze intent (already handled in STEP 1)
            # No additional action needed

    # TAB 2: History View
    with tab2:
        render_history_view()


if __name__ == "__main__":
    main()
