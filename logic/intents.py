"""
Intent Classification and Handling Logic

This module handles understanding user intentions and routing to the right action.

Student Guide:
--------------
Intent-Based Architecture:
1. User types something in chat
2. We classify their intent (what do they want?)
3. We route to the appropriate handler
4. Handler executes the action
5. We return a response to the user

This pattern is used in:
- Chatbots and virtual assistants
- Voice interfaces (Alexa, Siri)
- Command-line tools
- Any conversational interface
"""

import json
import logging
from typing import Dict, List
from llm.client import get_llm_client
from prompts.intent_prompts import (
    create_intent_classification_prompt,
    INTENT_CLASSIFICATION_SYSTEM_MESSAGE
)

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Classifies user messages into specific intents.

    Uses an LLM to understand natural language and determine:
    - What the user wants to do
    - Which companies they're talking about
    - Whether new analysis is needed

    Example usage:
        classifier = IntentClassifier()

        result = classifier.classify(
            user_message="Compare Tesla and Apple",
            analyzed_companies=["Tesla"]
        )

        print(result['intent'])  # "compare"
        print(result['companies'])  # ["Tesla", "Apple"]
        print(result['needs_analysis'])  # ["Apple"]
    """

    def __init__(self):
        """Initialize the intent classifier with an LLM client."""
        self.llm_client = get_llm_client()

    def classify(self, user_message: str, analyzed_companies: List[str]) -> Dict:
        """
        Classify a user message into an intent with extracted information.

        Args:
            user_message: What the user typed
            analyzed_companies: List of companies already in the database

        Returns:
            Dictionary with:
            - intent: The classified intent (analyze, compare, etc.)
            - companies: List of company names mentioned
            - question: The question if it's a rag_question, else None
            - needs_analysis: Companies that need analysis first

        Example:
            result = classifier.classify(
                "How does Tesla handle emissions?",
                ["Apple"]
            )
            # Returns: {
            #     "intent": "rag_question",
            #     "companies": ["Tesla"],
            #     "question": "How does Tesla handle emissions?",
            #     "needs_analysis": ["Tesla"]
            # }
        """
        logger.info(f"Classifying intent for: {user_message[:50]}...")

        try:
            # Create the classification prompt
            prompt = create_intent_classification_prompt(
                user_message,
                analyzed_companies
            )

            # Call LLM to classify
            response = self.llm_client.complete_json(
                prompt=prompt,
                system_message=INTENT_CLASSIFICATION_SYSTEM_MESSAGE,
                temperature=0.1  # Low temperature for consistent classification
            )

            # Parse JSON response
            intent_data = json.loads(response)

            logger.info(f"✓ Classified as: {intent_data.get('intent')}")
            return intent_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {str(e)}")
            # Fallback: treat as simple analysis
            return {
                'intent': 'analyze',
                'companies': [user_message.strip()],
                'question': None,
                'needs_analysis': [user_message.strip()]
            }

        except Exception as e:
            logger.error(f"Intent classification error: {str(e)}")
            # Fallback
            return {
                'intent': 'analyze',
                'companies': [user_message.strip()],
                'question': None,
                'needs_analysis': [user_message.strip()]
            }


# Singleton instance
_classifier_instance = None


def get_intent_classifier() -> IntentClassifier:
    """
    Get a singleton intent classifier instance.

    Returns:
        IntentClassifier instance

    Example:
        from logic.intents import get_intent_classifier

        classifier = get_intent_classifier()
        result = classifier.classify("Compare Tesla and Apple", [])
    """
    global _classifier_instance

    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()

    return _classifier_instance
