"""
Streamlit Configuration and Styling

This module contains all Streamlit page configuration and CSS styles.
Separating configuration makes it easy to:
- Update styles without touching app logic
- Maintain consistent styling across the app
- Share configuration between different pages

Student Guide:
--------------
Why separate configuration?
- Clean separation: UI config vs business logic
- Reusability: Import and use across multiple pages
- Maintainability: All styling in one place
"""

import streamlit as st


def setup_page_config():
    """
    Configure the Streamlit page settings.

    This sets up the page title, icon, layout, and sidebar state.
    Called once at the start of the app.

    Example:
        from ui.config import setup_page_config

        setup_page_config()
        # Now your page has the correct title and icon!
    """
    st.set_page_config(
        page_title="Sustainability Scorer",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def apply_custom_css():
    """
    Apply custom CSS styling to the Streamlit app.

    This function injects custom CSS to style chat messages
    and other UI elements.

    Why custom CSS?
    - Better visual design
    - Consistent spacing and colors
    - Professional appearance

    Example:
        from ui.config import apply_custom_css

        apply_custom_css()
        # Now your app has custom styling!
    """
    st.markdown("""
    <style>
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)


def get_initial_chat_message() -> str:
    """
    Get the initial welcome message for the chat interface.

    Returns:
        str: The welcome message with instructions

    Why a function?
    - Easy to update the message
    - Can be reused if chat is reset
    - Keeps message text separate from UI code
    """
    return """👋 Hi! I'm your sustainability analysis assistant. I can help you understand companies' ESG (Environmental, Social, Governance) performance.

**Just talk to me naturally! I can:**
✅ **Analyze companies**: "Check out Tesla"
✅ **Compare**: "Compare Tesla and Apple"
✅ **Get scores**: "What's Tesla's environmental score?"
✅ **Ask questions**: "How does Tesla handle carbon emissions?" (I'll use scraped data!)
✅ **Find strengths**: "What is Apple good at?"
✅ **Get details**: "Tell me more about Microsoft"
✅ **Manage**: "Delete Tesla" or use 🗑️ buttons in sidebar

I use real web data and AI to answer your questions! 🚀"""
