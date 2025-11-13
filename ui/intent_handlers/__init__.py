"""
Intent Handlers Module

This module contains all chat intent handlers.

Each handler is responsible for processing a specific type of user intent:
- analyze.py: Analyze new companies
- compare.py: Compare multiple companies
- rag.py: Answer questions using RAG (Retrieval Augmented Generation)
- scores.py: Show scores and details
- management.py: Delete/clear operations

Student Guide:
--------------
Why separate intent handlers?
- Each file has ONE responsibility
- Easy to understand what each handler does
- Easy to test independently
- Easy to add new intents (just add a new file!)
- Clean code organization

Example usage:
    from ui.intent_handlers import handle_analyze, handle_compare

    if intent == "analyze":
        handle_analyze(companies, needs_analysis)
    elif intent == "compare":
        handle_compare(companies)
"""

from ui.intent_handlers.analyze import handle_analyze
from ui.intent_handlers.compare import handle_compare
from ui.intent_handlers.rag import handle_rag_question
from ui.intent_handlers.scores import (
    handle_show_score,
    handle_show_details,
    handle_show_category,
    handle_show_strengths_weaknesses
)
from ui.intent_handlers.management import (
    handle_delete,
    handle_clear,
    handle_list_companies
)

__all__ = [
    'handle_analyze',
    'handle_compare',
    'handle_rag_question',
    'handle_show_score',
    'handle_show_details',
    'handle_show_category',
    'handle_show_strengths_weaknesses',
    'handle_delete',
    'handle_clear',
    'handle_list_companies'
]
