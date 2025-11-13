"""
Sustainability Scorer - Calculates Final ESG Scores

This module takes the raw metrics extracted by the extractor and calculates:
1. Weighted scores for each category (Environmental, Social, Governance)
2. Final overall sustainability score (0-100)
3. Qualitative ratings (Excellent, Good, Fair, Poor, Very Poor)
4. Recommendations for improvement

Student Guide:
--------------
Key Concepts:
- Weighted Average: Different categories have different importance
  * Environmental: 40% of final score
  * Social: 35% of final score
  * Governance: 25% of final score

- Confidence Weighting: Metrics with higher confidence have more influence
  * High confidence (0.9) = trustworthy data
  * Low confidence (0.3) = uncertain data

Main Functions:
- calculate_category_score(): Scores one category (e.g., Environmental)
- calculate_final_score(): Combines all categories into overall score
- get_recommendations(): Suggests improvements based on weak areas
"""

import logging
from typing import Dict, List
from datetime import datetime

# Setup logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SustainabilityScorer:
    """
    Calculates sustainability scores from extracted metrics.

    The scoring system:
    1. Takes metrics from each category (Environmental, Social, Governance)
    2. Weights them by confidence (more reliable metrics count more)
    3. Applies category weights to get final score
    4. Provides qualitative rating and recommendations

    Example usage:
        scorer = SustainabilityScorer()
        scores = scorer.calculate_final_score(metrics)
        print(f"Final Score: {scores['final_score']}/100")
        print(f"Rating: {scores['score_level']}")
    """

    # How much each category contributes to the final score
    # These weights must add up to 1.0 (100%)
    CATEGORY_WEIGHTS = {
        "Environmental": 0.40,  # 40% of final score
        "Social": 0.35,         # 35% of final score
        "Governance": 0.25      # 25% of final score
    }

    # Qualitative ratings based on numerical scores
    SCORE_LEVELS = {
        "Excellent": (85, 100),   # 85-100 points
        "Good": (70, 84),          # 70-84 points
        "Fair": (50, 69),          # 50-69 points
        "Poor": (30, 49),          # 30-49 points
        "Very Poor": (0, 29)       # 0-29 points
    }

    def __init__(self):
        """Initialize the Sustainability Scorer."""
        logger.info("Sustainability Scorer initialized")

    def calculate_category_score(self, metrics: List[Dict], category: str) -> Dict:
        """
        Calculate the score for ONE category (e.g., Environmental).

        How it works:
        1. Filters metrics to only this category
        2. Calculates confidence-weighted average:
           - High confidence metrics have more influence
           - Low confidence metrics have less influence
        3. Returns category score and details

        Args:
            metrics: List of all metrics from all categories
            category: Which category to score ("Environmental", "Social", or "Governance")

        Returns:
            Dictionary with:
            - score: Category score (0-100)
            - confidence: Average confidence level (0-1)
            - metric_count: How many metrics were used
            - metrics: Individual metric details

        Example:
            # Get only Environmental metrics
            env_score = scorer.calculate_category_score(all_metrics, "Environmental")
            print(f"Environmental: {env_score['score']}/100")
        """
        # Step 1: Filter to only this category's metrics
        category_metrics = [m for m in metrics if m['category'] == category]

        # Step 2: Handle case where no metrics found
        if not category_metrics:
            logger.warning(f"⚠️ No metrics found for category: {category}")
            return {
                'score': 50.0,           # Neutral score (middle of range)
                'confidence': 0.0,       # No confidence (no data)
                'metric_count': 0,
                'metrics': []
            }

        # Step 3: Calculate confidence-weighted average
        # Formula: score = Σ(value × confidence) / Σ(confidence)
        total_weighted_score = 0
        total_confidence = 0

        for metric in category_metrics:
            # Get metric value and confidence
            confidence = metric.get('confidence', 0.5)  # Default 0.5 if missing
            value = metric.get('value', 50)             # Default 50 if missing

            # Add to weighted sum
            total_weighted_score += value * confidence
            total_confidence += confidence

        # Step 4: Calculate final category score
        if total_confidence > 0:
            # Weighted average
            category_score = total_weighted_score / total_confidence
            # Average confidence across all metrics
            avg_confidence = total_confidence / len(category_metrics)
        else:
            # No valid confidence values, use neutral score
            category_score = 50.0
            avg_confidence = 0.0

        # Step 5: Format individual metric details for output
        metric_details = [
            {
                'name': m['metric_name'],
                'value': m['value'],
                'confidence': m['confidence']
            }
            for m in category_metrics
        ]

        # Step 6: Return results
        return {
            'score': round(category_score, 2),
            'confidence': round(avg_confidence, 2),
            'metric_count': len(category_metrics),
            'metrics': metric_details
        }

    def calculate_final_score(self, metrics: List[Dict]) -> Dict:
        """
        Calculate the final weighted sustainability score.

        This is the main scoring function. It:
        1. Calculates scores for each category
        2. Applies category weights (Environmental 40%, Social 35%, Governance 25%)
        3. Combines into final score
        4. Adds qualitative rating
        5. Packages all results

        Args:
            metrics: List of ALL extracted metrics from all categories

        Returns:
            Comprehensive scoring dictionary with:
            - final_score: Overall score (0-100)
            - score_level: Rating (Excellent, Good, Fair, Poor, Very Poor)
            - environmental_score, social_score, governance_score
            - category_breakdown: Detailed per-category results
            - component_scores: Flattened scores for easy access

        Example:
            metrics = [
                {"category": "Environmental", "metric_name": "Carbon", "value": 85, "confidence": 0.9},
                {"category": "Social", "metric_name": "Labor", "value": 70, "confidence": 0.8},
                ...
            ]
            scores = scorer.calculate_final_score(metrics)
            print(f"Final: {scores['final_score']}/100 - {scores['score_level']}")
        """
        logger.info("📊 Calculating final sustainability score...")

        # STEP 1: Calculate scores for each category
        category_scores = {}
        weighted_sum = 0
        total_weight = 0

        for category, weight in self.CATEGORY_WEIGHTS.items():
            # Get category score
            category_data = self.calculate_category_score(metrics, category)
            category_scores[category] = category_data

            # Apply category weight to get contribution to final score
            # Example: Environmental score 80 × weight 0.40 = 32 points
            weighted_sum += category_data['score'] * weight
            total_weight += weight

        # STEP 2: Calculate final weighted score
        if total_weight > 0:
            final_score = weighted_sum / total_weight
        else:
            final_score = 50.0  # Neutral score if no data

        # STEP 3: Determine qualitative score level
        score_level = self._get_score_level(final_score)

        # STEP 4: Calculate overall confidence
        # Average of all category confidences
        avg_confidence = sum(
            cat['confidence'] for cat in category_scores.values()
        ) / len(category_scores)

        # STEP 5: Build comprehensive result package
        result = {
            # Main scores
            'final_score': round(final_score, 2),
            'score_level': score_level,
            'confidence': round(avg_confidence, 2),

            # Individual category scores (for quick access)
            'environmental_score': category_scores['Environmental']['score'],
            'social_score': category_scores['Social']['score'],
            'governance_score': category_scores['Governance']['score'],

            # Detailed category breakdown
            'category_breakdown': category_scores,

            # Flattened component scores (for database storage)
            'component_scores': self._build_component_scores(category_scores),

            # Timestamp
            'calculated_at': datetime.now().isoformat()
        }

        logger.info(f"✅ Final score: {final_score:.2f}/100 ({score_level})")
        return result

    def _get_score_level(self, score: float) -> str:
        """
        Convert numerical score to qualitative rating.

        Score ranges:
        - 85-100: Excellent (industry leader)
        - 70-84:  Good (above average)
        - 50-69:  Fair (average)
        - 30-49:  Poor (below average)
        - 0-29:   Very Poor (major issues)

        Args:
            score: Numerical score (0-100)

        Returns:
            Qualitative level string

        Example:
            level = scorer._get_score_level(78)
            # Returns: "Good"
        """
        for level, (min_score, max_score) in self.SCORE_LEVELS.items():
            if min_score <= score <= max_score:
                return level
        return "Unknown"

    def _build_component_scores(self, category_scores: Dict) -> Dict:
        """
        Flatten scores into a simple dictionary for easy database storage.

        Takes the nested category_scores structure and converts it to
        flat key-value pairs like: {"environmental_overall": 85, "carbon": 90, ...}

        Args:
            category_scores: Nested dictionary with category details

        Returns:
            Flattened dictionary with all scores

        Example:
            Input: {"Environmental": {"score": 85, "metrics": [{"name": "Carbon", "value": 90}]}}
            Output: {"environmental_overall": 85, "carbon": 90}
        """
        component_scores = {}

        for category, data in category_scores.items():
            # Add category-level score
            # e.g., "environmental_overall" = 85
            key = f"{category.lower()}_overall"
            component_scores[key] = data['score']

            # Add individual metric scores
            for metric in data['metrics']:
                # Create safe key name (lowercase, no spaces)
                # e.g., "Carbon Emissions Reduction" → "carbon_emissions_reduction"
                metric_key = (
                    metric['name']
                    .lower()
                    .replace(' ', '_')
                    .replace('and', '')
                    .replace('__', '_')
                    .strip('_')
                )
                component_scores[metric_key] = metric['value']

        return component_scores

    def get_recommendations(self, scores: Dict) -> List[str]:
        """
        Generate improvement recommendations based on scores.

        Analyzes the scores and suggests which areas need the most attention.
        Prioritizes:
        1. Low category scores (< 60)
        2. Low individual metrics (< 50)
        3. Overall score level

        Args:
            scores: Complete scores dictionary from calculate_final_score()

        Returns:
            List of recommendation strings (up to 5)

        Example:
            recommendations = scorer.get_recommendations(scores)
            for rec in recommendations:
                print(f"- {rec}")

            # Output:
            # - Priority: Improve Social practices (current score: 55/100)
            # - Focus on: Labor Practices in Social category (score: 45/100)
        """
        recommendations = []

        # Check each category for low scores
        for category in ['Environmental', 'Social', 'Governance']:
            category_data = scores['category_breakdown'][category]
            score = category_data['score']

            # If category score is low (< 60), prioritize it
            if score < 60:
                recommendations.append(
                    f"Priority: Improve {category} practices (current score: {score:.1f}/100)"
                )

            # Find low-scoring metrics within this category
            low_metrics = [
                m for m in category_data['metrics']
                if m['value'] < 50
            ]

            # Add recommendations for top 2 lowest metrics
            for metric in low_metrics[:2]:
                recommendations.append(
                    f"Focus on: {metric['name']} in {category} category (score: {metric['value']:.1f}/100)"
                )

        # Add overall recommendation based on final score
        if scores['final_score'] < 50:
            recommendations.insert(
                0,
                "Critical: Significant improvements needed across all sustainability areas"
            )
        elif scores['final_score'] < 70:
            recommendations.insert(
                0,
                "Important: Enhance sustainability practices to meet industry standards"
            )

        # Return top 5 recommendations
        return recommendations[:5]


def test_sustainability_scorer():
    """
    Test the Sustainability Scorer with sample data.

    This test:
    1. Creates sample metrics for a fictional company
    2. Calculates all scores
    3. Displays the results
    4. Generates recommendations
    """
    print("=" * 70)
    print("TESTING SUSTAINABILITY SCORER")
    print("=" * 70)

    try:
        # Create scorer instance
        scorer = SustainabilityScorer()
        print("✓ Scorer initialized\n")

        # Sample metrics (15 total: 5 per category)
        test_metrics = [
            # Environmental (40% of final score)
            {"category": "Environmental", "metric_name": "Carbon Emissions", "value": 85, "confidence": 0.9},
            {"category": "Environmental", "metric_name": "Renewable Energy", "value": 90, "confidence": 0.95},
            {"category": "Environmental", "metric_name": "Waste Management", "value": 75, "confidence": 0.8},
            {"category": "Environmental", "metric_name": "Water Conservation", "value": 70, "confidence": 0.7},
            {"category": "Environmental", "metric_name": "Sustainable Materials", "value": 65, "confidence": 0.6},

            # Social (35% of final score)
            {"category": "Social", "metric_name": "Labor Practices", "value": 80, "confidence": 0.85},
            {"category": "Social", "metric_name": "Diversity and Inclusion", "value": 75, "confidence": 0.8},
            {"category": "Social", "metric_name": "Community Impact", "value": 70, "confidence": 0.75},
            {"category": "Social", "metric_name": "Human Rights", "value": 85, "confidence": 0.9},
            {"category": "Social", "metric_name": "Employee Well-being", "value": 78, "confidence": 0.82},

            # Governance (25% of final score)
            {"category": "Governance", "metric_name": "Board Independence", "value": 72, "confidence": 0.75},
            {"category": "Governance", "metric_name": "Ethics and Compliance", "value": 88, "confidence": 0.9},
            {"category": "Governance", "metric_name": "Transparency", "value": 82, "confidence": 0.85},
            {"category": "Governance", "metric_name": "Risk Management", "value": 76, "confidence": 0.78},
            {"category": "Governance", "metric_name": "Stakeholder Engagement", "value": 74, "confidence": 0.76}
        ]

        # Calculate scores
        result = scorer.calculate_final_score(test_metrics)

        # Display results
        print("=" * 70)
        print("FINAL SCORES")
        print("=" * 70)
        print(f"Overall Score: {result['final_score']}/100")
        print(f"Rating: {result['score_level']}")
        print(f"Confidence: {result['confidence']}\n")

        print("=" * 70)
        print("CATEGORY SCORES")
        print("=" * 70)
        print(f"Environmental: {result['environmental_score']}/100 (weight: 40%)")
        print(f"Social: {result['social_score']}/100 (weight: 35%)")
        print(f"Governance: {result['governance_score']}/100 (weight: 25%)\n")

        print("=" * 70)
        print("CATEGORY BREAKDOWN")
        print("=" * 70)
        for category, data in result['category_breakdown'].items():
            print(f"\n{category}:")
            print(f"  Score: {data['score']}/100")
            print(f"  Confidence: {data['confidence']}")
            print(f"  Metrics analyzed: {data['metric_count']}")

        # Generate recommendations
        recommendations = scorer.get_recommendations(result)
        print("\n" + "=" * 70)
        print(f"RECOMMENDATIONS ({len(recommendations)})")
        print("=" * 70)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

        # Validate results
        assert 0 <= result['final_score'] <= 100, "Final score out of range!"
        print("\n" + "=" * 70)
        print("✅ TEST PASSED: All scores calculated correctly")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


# When this file is run directly, run the test
if __name__ == "__main__":
    test_sustainability_scorer()
