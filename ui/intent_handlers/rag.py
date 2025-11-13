"""
RAG Question Intent Handler

Handles the "rag_question" intent - answering questions using scraped data.

Student Guide:
--------------
RAG = Retrieval Augmented Generation

This means:
1. We retrieve relevant information (scraped sources)
2. We augment the AI prompt with this information
3. We generate an answer based on the provided context

Why RAG?
- More accurate than asking AI from memory alone
- Can cite specific sources
- Based on actual company data we scraped
- Up-to-date information

Example:
    User: "How does Tesla handle carbon emissions?"

    We:
    1. Get Tesla's scraped sources from database
    2. Create prompt with sources as context
    3. AI answers based on the sources
    4. Return answer with score context
"""

import streamlit as st
from typing import List
from ui.components.sidebar import get_companies_from_db
from llm.client import get_llm_client
from prompts.rag_prompts import create_rag_answer_prompt, create_rag_system_message


def handle_rag_question(companies: List[str], question: str):
    """
    Handle RAG question intent - answer question using scraped data.

    This function:
    1. Fetches company's scraped sources from database
    2. Creates context from top 3 sources
    3. Uses LLM to answer question based on context
    4. Adds answer with score context to chat

    Args:
        companies: List of company names (usually just one)
        question: The user's question

    Example:
        handle_rag_question(
            ["Tesla"],
            "How does Tesla handle carbon emissions?"
        )
        # Answers based on Tesla's scraped sources
    """
    company_name = companies[0] if companies else None
    if not company_name:
        response = "Please specify a company for your question."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    # Company should already be analyzed (handled in analyze step)
    companies_data = get_companies_from_db()
    if company_name not in companies_data:
        response = f"Something went wrong - {company_name} should have been analyzed already."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    data = companies_data[company_name]

    with st.chat_message("assistant"):
        with st.spinner(f"🤔 Thinking about your question..."):
            # Prepare context from scraped sources (top 3)
            context = "\n\n---\n\n".join([
                f"Source: {s['url']}\n{s['content'][:3000]}"
                for s in data['sources'][:3]
            ])

            # Use centralized LLM client and prompts
            llm_client = get_llm_client()

            try:
                # Create RAG prompt using centralized prompt module
                prompt = create_rag_answer_prompt(company_name, question, context)
                system_message = create_rag_system_message(company_name)

                # Call LLM using centralized client
                answer = llm_client.complete(
                    prompt=prompt,
                    system_message=system_message,
                    temperature=0.3,
                    max_tokens=500
                )

                response = f"**Regarding {company_name}:**\n\n{answer}\n\n"

                # Add score context
                scores = data['scores']
                response += f"\n*Based on our analysis, {company_name} has an overall sustainability score of {scores['final_score']:.1f}/100.*"

            except Exception as e:
                response = f"I couldn't generate an answer: {str(e)}"

    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()
