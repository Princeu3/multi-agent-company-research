"""
UI Module

This module contains all Streamlit UI components and handlers.

Structure:
----------
ui/
 config.py                 # Streamlit configuration and CSS
 components/               # Reusable UI components
    sidebar.py           # Sidebar with company list
    chat_interface.py    # Chat UI helpers
    history_view.py      # History table view
 intent_handlers/          # Chat intent handlers
     analyze.py           # Analyze companies
     compare.py           # Compare companies
     rag.py               # RAG questions
     scores.py            # Score displays
     management.py        # Delete/clear operations

Student Guide:
--------------
Why this structure?
- Separation of concerns: Each file has ONE job
- Easy to understand: Clear folder structure
- Easy to test: Test each component independently
- Easy to extend: Add new components/handlers easily
- Clean code: No monolithic files!

Example usage:
    from ui.config import setup_page_config
    from ui.components.sidebar import render_sidebar
    from ui.intent_handlers import handle_analyze

    setup_page_config()
    render_sidebar()
    handle_analyze(["Tesla"])
"""

__version__ = "1.0.0"
