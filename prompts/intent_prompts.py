"""
Prompts for Intent Classification

This module contains prompts for understanding user intentions in the chat interface.
The AI reads user messages and classifies them into specific intents (analyze, compare, etc.)

Student Guide:
--------------
Intent Classification: Understanding what the user wants to do
- User says "Check out Tesla" → Intent: analyze
- User says "Compare Tesla and Apple" → Intent: compare
- User says "How does Tesla handle emissions?" → Intent: rag_question

This is crucial for building conversational interfaces!
"""

from typing import List


def create_intent_classification_prompt(user_message: str, analyzed_companies: List[str]) -> str:
    """
    Create prompt for classifying user intent from their message.

    The LLM analyzes the user's message and determines:
    1. What they want to do (intent)
    2. Which companies they're asking about
    3. Whether it's a question (for RAG)
    4. Which companies need analysis first

    Args:
        user_message: What the user typed in the chat
        analyzed_companies: List of companies already in the database

    Returns:
        Prompt string that will return structured JSON with intent classification

    Example:
        analyzed = ["Tesla", "Apple"]
        prompt = create_intent_classification_prompt("Compare Tesla and Microsoft", analyzed)
        # Will classify as "compare" intent with needs_analysis=["Microsoft"]
    """
    analyzed_companies_str = ', '.join(analyzed_companies) if analyzed_companies else "None"

    prompt = f"""You are an intent classifier for a sustainability analysis chatbot.
Analyze the user's message and return a JSON object with the following structure:

{{
    "intent": "one of: analyze, compare, rag_question, show_score, show_details, show_environmental, show_social, show_governance, show_strengths_weaknesses, list_companies, delete, clear",
    "companies": ["list of company names mentioned"],
    "question": "the actual question if it's a rag_question, otherwise null",
    "needs_analysis": ["list of companies that need to be analyzed first"]
}}

Already analyzed companies in database: {analyzed_companies_str}

INTENT DEFINITIONS:
-------------------
- "analyze": User wants to analyze a new company's sustainability
- "compare": User wants to compare 2+ companies
- "rag_question": User is asking a specific question about a company (use scraped data to answer)
- "show_score": User wants to see the overall or category score
- "show_details": User wants detailed analysis
- "show_environmental/social/governance": User wants specific category info
- "show_strengths_weaknesses": User wants to know pros/cons
- "list_companies": User wants to see all analyzed companies
- "delete": User wants to delete specific company/companies from the database
- "clear": User wants to clear/reset everything (delete all)

NEEDS_ANALYSIS FIELD:
---------------------
Include companies that are mentioned but NOT in the already analyzed list.
These companies need to be analyzed before we can answer the user's query.

EXAMPLES:
---------
User: "Tesla"
Output: {{"intent": "analyze", "companies": ["Tesla"], "question": null, "needs_analysis": ["Tesla"]}}

User: "Compare Tesla and Apple"
Output: {{"intent": "compare", "companies": ["Tesla", "Apple"], "question": null, "needs_analysis": ["Tesla", "Apple"] if not analyzed}}

User: "How does Tesla handle carbon emissions?"
Output: {{"intent": "rag_question", "companies": ["Tesla"], "question": "How does Tesla handle carbon emissions?", "needs_analysis": ["Tesla"] if not analyzed}}

User: "What's Apple's environmental score?"
Output: {{"intent": "show_environmental", "companies": ["Apple"], "question": null, "needs_analysis": ["Apple"] if not analyzed}}

User: "Delete Tesla"
Output: {{"intent": "delete", "companies": ["Tesla"], "question": null, "needs_analysis": []}}

USER MESSAGE TO CLASSIFY:
{user_message}

Return ONLY valid JSON, no other text.
"""
    return prompt


# System message for intent classification
INTENT_CLASSIFICATION_SYSTEM_MESSAGE = "You are an intent classification expert for a sustainability chatbot. Return only valid JSON."
