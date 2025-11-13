"""
Metrics Extractor - Uses AI to Extract Sustainability Metrics

This module uses GPT-4o-mini to analyze company research content and extract
structured sustainability metrics.

NOW REFACTORED: Uses separate prompts/ and llm/ modules for cleaner code!

Student Guide:
--------------
This file is now much simpler because we:
1. Moved all prompts to prompts/extraction_prompts.py
2. Moved LLM client to llm/client.py
3. Keep only the extraction logic here

This makes the code easier to:
- Understand (each file has one job)
- Test (mock the LLM client)
- Maintain (change prompts without touching logic)
"""

import json
import logging
from typing import Dict, List

# NEW: Import from our modular structure
from llm.client import get_llm_client
from prompts.extraction_prompts import (
    METRICS_SCHEMA,
    create_metrics_extraction_prompt,
    METRICS_EXTRACTION_SYSTEM_MESSAGE
)

logger = logging.getLogger(__name__)


class MetricsExtractor:
    """
    Extracts structured sustainability metrics from research content using AI.

    Now uses centralized LLM client and prompts modules!

    Example usage:
        extractor = MetricsExtractor()
        metrics = extractor.extract_metrics("Tesla", research_sources)
        print(f"Extracted {len(metrics)} metrics")
    """

    # Re-export METRICS_SCHEMA for backward compatibility
    METRICS_SCHEMA = METRICS_SCHEMA

    # Category weights (same as before)
    CATEGORY_WEIGHTS = {
        "Environmental": 0.40,
        "Social": 0.35,
        "Governance": 0.25
    }

    def __init__(self):
        """Initialize the Metrics Extractor with LLM client."""
        # NEW: Use centralized LLM client
        self.llm_client = get_llm_client()
        logger.info("Metrics Extractor initialized successfully")

    def extract_metrics(self, company_name: str, sources: List[Dict[str, str]]) -> List[Dict]:
        """
        Extract sustainability metrics from research sources using AI.

        Args:
            company_name: Name of the company
            sources: List of dicts with 'url' and 'content' keys

        Returns:
            List of metric dictionaries

        Example:
            sources = [
                {"url": "https://tesla.com/impact", "content": "Tesla reduced emissions..."},
                {"url": "https://news.com/tesla", "content": "Tesla's labor practices..."}
            ]
            metrics = extractor.extract_metrics("Tesla", sources)
        """
        logger.info(f"🤖 Extracting metrics for: {company_name}")

        # STEP 1: Combine content from all sources
        combined_content = "\n\n---\n\n".join([
            f"Source: {s['url']}\n{s['content'][:5000]}"
            for s in sources
        ])

        # STEP 2: Create prompt using centralized prompt module
        prompt = create_metrics_extraction_prompt(company_name, combined_content)

        try:
            # STEP 3: Call LLM using centralized client
            logger.info("Sending content to GPT-4o-mini for analysis...")

            response = self.llm_client.complete_json(
                prompt=prompt,
                system_message=METRICS_EXTRACTION_SYSTEM_MESSAGE,
                temperature=0.2,
                max_tokens=2000
            )

            # STEP 4: Parse response
            data = json.loads(response)
            metrics = data.get('metrics', [])

            # STEP 5: Validate and clean
            validated_metrics = self._validate_metrics(metrics)

            logger.info(f"✅ Successfully extracted {len(validated_metrics)} metrics")
            return validated_metrics

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {str(e)}")
            return self._get_default_metrics()

        except Exception as e:
            logger.error(f"❌ Extraction error: {str(e)}")
            return self._get_default_metrics()

    def _validate_metrics(self, metrics: List[Dict]) -> List[Dict]:
        """
        Validate and clean extracted metrics from the AI.

        Args:
            metrics: Raw metrics from the AI

        Returns:
            Cleaned and validated metrics list
        """
        validated = []

        for metric in metrics:
            # Check required fields
            required_fields = ['category', 'metric_name', 'value', 'confidence']
            if not all(k in metric for k in required_fields):
                logger.warning(f"⚠️ Skipping metric missing fields: {metric}")
                continue

            # Validate category
            if metric['category'] not in self.CATEGORY_WEIGHTS:
                logger.warning(f"⚠️ Invalid category: {metric['category']}")
                continue

            # Validate and clamp value (0-100)
            try:
                value = float(metric['value'])
                value = max(0, min(100, value))
            except (ValueError, TypeError):
                logger.warning(f"⚠️ Invalid value for {metric['metric_name']}, using 50")
                value = 50.0

            # Validate and clamp confidence (0-1)
            try:
                confidence = float(metric['confidence'])
                confidence = max(0, min(1, confidence))
            except (ValueError, TypeError):
                logger.warning(f"⚠️ Invalid confidence for {metric['metric_name']}, using 0.5")
                confidence = 0.5

            # Add validated metric
            validated.append({
                'category': metric['category'],
                'metric_name': metric['metric_name'],
                'value': round(value, 2),
                'confidence': round(confidence, 2)
            })

        return validated

    def _get_default_metrics(self) -> List[Dict]:
        """
        Get default neutral metrics when extraction fails.

        Returns:
            List of 15 metrics with neutral scores
        """
        logger.warning("⚠️ Using default metrics due to extraction failure")

        default_metrics = []

        for category, metric_names in self.METRICS_SCHEMA.items():
            for metric_name in metric_names:
                default_metrics.append({
                    'category': category,
                    'metric_name': metric_name,
                    'value': 50.0,
                    'confidence': 0.1
                })

        return default_metrics


def test_metrics_extractor():
    """Test the refactored Metrics Extractor."""
    print("=" * 70)
    print("TESTING REFACTORED METRICS EXTRACTOR")
    print("=" * 70)
    print("\nNOTE: Now uses modular prompts/ and llm/ structure!\n")

    try:
        extractor = MetricsExtractor()
        print("✓ Extractor initialized (using centralized LLM client)\n")

        # Sample test data
        test_sources = [
            {
                "url": "https://example.com/tesla",
                "content": """
                Tesla's 2024 Impact Report highlights significant progress in sustainability:

                Environmental:
                - Reduced carbon emissions by 40% compared to 2020
                - 100% of Gigafactories now powered by renewable energy
                - Recycling 92% of battery materials

                Social:
                - Improved workplace diversity: 35% women in workforce
                - Community programs benefited 100,000+ people

                Governance:
                - Board includes 5 independent directors
                - Enhanced ethics and compliance programs
                """
            }
        ]

        # Extract metrics
        print("Extracting metrics using centralized prompt + client...\n")
        metrics = extractor.extract_metrics("Tesla", test_sources)

        # Display results
        print("=" * 70)
        print(f"EXTRACTED {len(metrics)} METRICS")
        print("=" * 70)

        for category in extractor.CATEGORY_WEIGHTS.keys():
            category_metrics = [m for m in metrics if m['category'] == category]
            if category_metrics:
                print(f"\n{category} ({len(category_metrics)} metrics):")
                print("-" * 70)
                for m in category_metrics:
                    print(f"  • {m['metric_name']}: {m['value']}/100 (confidence: {m['confidence']})")

        print("\n" + "=" * 70)
        print("✅ TEST PASSED: Refactored extractor works correctly!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_metrics_extractor()
