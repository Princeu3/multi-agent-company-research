"""
Chat Interface Component

This module handles the chat UI display and message input.

Student Guide:
--------------
The chat interface:
- Displays conversation history
- Handles user input
- Routes messages to intent handlers
- Updates chat history

Why separate the chat interface?
- Clean UI code separated from intent handling logic
- Easy to modify chat display without touching business logic
- Can test UI independently
- Reusable across different pages
"""

import streamlit as st
from logic.intents import get_intent_classifier
from ui.components.sidebar import get_companies_from_db


def initialize_chat_state(initial_message: str):
    """
    Initialize chat session state if not already initialized.

    Args:
        initial_message: The welcome message to display

    Example:
        initialize_chat_state("Welcome to the chat!")
    """
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": initial_message}
        ]


def display_chat_messages():
    """
    Display all chat messages from session state.

    This function renders all messages in the chat history,
    with proper formatting for user and assistant messages.

    Example:
        display_chat_messages()
        # Shows all messages in the conversation
    """
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def classify_user_intent(user_message: str) -> dict:
    """
    Classify user's intent from their message.

    Uses the centralized intent classifier to understand what
    the user wants to do.

    Args:
        user_message: What the user typed

    Returns:
        dict: Intent data with intent, companies, question, needs_analysis

    Example:
        intent_data = classify_user_intent("Compare Tesla and Apple")
        # Returns: {
        #     "intent": "compare",
        #     "companies": ["Tesla", "Apple"],
        #     "question": None,
        #     "needs_analysis": ["Tesla", "Apple"]
        # }
    """
    # Get list of already analyzed companies from database
    companies_data = get_companies_from_db()
    analyzed_companies = list(companies_data.keys())

    # Use centralized intent classifier
    classifier = get_intent_classifier()
    intent_data = classifier.classify(user_message, analyzed_companies)

    return intent_data


def add_user_message(message: str):
    """
    Add a user message to the chat history.

    Args:
        message: The user's message

    Example:
        add_user_message("What's Tesla's score?")
    """
    st.session_state.chat_messages.append({"role": "user", "content": message})


def add_assistant_message(message: str):
    """
    Add an assistant message to the chat history.

    Args:
        message: The assistant's message

    Example:
        add_assistant_message("Tesla's score is 63.5/100")
    """
    st.session_state.chat_messages.append({"role": "assistant", "content": message})
