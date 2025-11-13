"""
Prompts for RAG (Retrieval Augmented Generation)

RAG = Using retrieved documents as context to answer questions
This is more accurate than asking the AI to answer from memory alone.

Student Guide:
--------------
How RAG Works:
1. User asks: "How does Tesla handle carbon emissions?"
2. We retrieve: Scraped content about Tesla (our "context")
3. We send to AI: Context + Question
4. AI answers: Based on the provided context (not memory)

This ensures:
- Answers are based on real data
- We can cite sources
- More accurate than pure LLM answers
"""


def create_rag_answer_prompt(company_name: str, question: str, context: str) -> str:
    """
    Create prompt for answering questions using RAG (Retrieval Augmented Generation).

    Takes the user's question and relevant context (scraped content) and asks
    the AI to answer based ONLY on the provided context.

    Args:
        company_name: Name of the company
        question: User's question
        context: Relevant scraped content (from top 3 sources)

    Returns:
        Prompt that will produce an answer based on the context

    Example:
        context = "Tesla reduced emissions by 40%... Gigafactories use 100% renewable energy..."
        question = "How does Tesla handle carbon emissions?"
        prompt = create_rag_answer_prompt("Tesla", question, context)
        # AI will answer based on the provided context
    """
    prompt = f"""Research content about {company_name}:

{context}

Question: {question}

Answer the question based on the research content provided above. Be specific and cite information from the sources when possible. If the information isn't in the sources, say so clearly.
"""
    return prompt


def create_rag_system_message(company_name: str) -> str:
    """
    Create system message for RAG question answering.

    The system message sets the AI's role and behavior.

    Args:
        company_name: Name of the company being discussed

    Returns:
        System message string
    """
    return f"You are a sustainability analyst. Answer the user's question about {company_name} based on the provided research content. Be specific and cite information from the sources when possible. If the information isn't in the sources, say so."
