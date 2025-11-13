"""
Prompts for Metrics Extraction using LLMs

This module contains all prompts used to extract sustainability metrics
from research content. Separating prompts makes them easy to:
- Update and improve
- A/B test different versions
- Version control independently
- Understand what we're asking the AI to do

Student Guide:
--------------
Prompt Engineering: The art of writing clear instructions for AI models
- Be specific about what you want
- Provide examples and guidelines
- Define the output format clearly
- Include constraints and edge cases
"""

# Metrics schema - what metrics to extract
METRICS_SCHEMA = {
    "Environmental": [
        "Carbon Emissions Reduction",
        "Renewable Energy Usage",
        "Waste Management",
        "Water Conservation",
        "Sustainable Materials"
    ],
    "Social": [
        "Labor Practices",
        "Diversity and Inclusion",
        "Community Impact",
        "Human Rights",
        "Employee Well-being"
    ],
    "Governance": [
        "Board Independence",
        "Ethics and Compliance",
        "Transparency and Reporting",
        "Risk Management",
        "Stakeholder Engagement"
    ]
}


def create_metrics_extraction_prompt(company_name: str, content: str) -> str:
    """
    Create the prompt for extracting sustainability metrics from research content.

    This prompt asks the AI to:
    1. Read the company research content
    2. Find information about specific sustainability practices
    3. Score each practice (0-100)
    4. Assess confidence in each score (0-1)
    5. Return structured JSON output

    Args:
        company_name: Name of the company being analyzed
        content: Combined research content from all sources (max 15,000 chars)

    Returns:
        Complete prompt string ready to send to the LLM

    Example:
        prompt = create_metrics_extraction_prompt("Tesla", research_content)
        response = llm_client.complete(prompt)
    """
    # Build formatted list of all metrics
    metrics_list = []
    for category, metrics in METRICS_SCHEMA.items():
        metrics_list.append(f"\n{category}:")
        for metric in metrics:
            metrics_list.append(f"  - {metric}")

    # Create the full prompt with clear instructions
    prompt = f"""You are an expert sustainability analyst. Analyze the following content about {company_name} and extract sustainability metrics.

For each metric, provide:
1. A score from 0-100 (where 0 = very poor, 50 = average, 100 = excellent)
2. A confidence score from 0-1 (where 0 = no data/uncertain, 1 = very confident)

Extract metrics for these categories and specific metrics:
{''.join(metrics_list)}

SCORING GUIDELINES:
-------------------
90-100: Industry-leading, exceptional performance
75-89:  Strong performance, above average
60-74:  Good performance, meeting standards
40-59:  Fair performance, some concerns
20-39:  Poor performance, significant issues
0-19:   Very poor performance, major problems

CONFIDENCE GUIDELINES:
----------------------
0.9-1.0:  Direct data, official reports, verified sources
0.7-0.89: Strong indirect evidence, credible sources
0.5-0.69: Some evidence, moderate certainty
0.3-0.49: Limited evidence, low certainty
0-0.29:   No clear evidence, speculation

IMPORTANT: If a metric has no information in the content, use score=50 (neutral) and confidence=0.1 (very uncertain).

Return ONLY a JSON object with this exact structure (no extra text):
{{
    "metrics": [
        {{
            "category": "Environmental|Social|Governance",
            "metric_name": "exact metric name from list above",
            "value": 0-100,
            "confidence": 0-1,
            "evidence": "brief quote or summary of evidence"
        }}
    ]
}}

RESEARCH CONTENT TO ANALYZE:
{content[:15000]}
"""
    return prompt


# System message for metrics extraction
METRICS_EXTRACTION_SYSTEM_MESSAGE = "You are a sustainability metrics extraction expert. Return only valid JSON."
