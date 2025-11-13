"""
PDF Report Generator for Company Sustainability Reports

This module generates professional PDF reports for:
1. Single company sustainability analysis
2. Multi-company comparison reports

Uses ReportLab for PDF generation with professional formatting.

Student Guide:
--------------
Key Concepts:
- ReportLab: Python library for creating PDFs programmatically
- Canvas: Drawing surface for adding text, shapes, and images
- Styles: Formatting for text (fonts, sizes, colors)
- Tables: Structured data display with borders and alignment

Main Functions:
- generate_single_company_report(): Create PDF for one company
- generate_comparison_report(): Create PDF comparing multiple companies
"""

import io
import logging
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Setup logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Generates professional PDF reports for company sustainability analysis.

    Features:
    - Single company detailed reports with scores and metrics
    - Multi-company comparison reports with side-by-side analysis
    - Professional formatting with tables, colors, and headers
    - Automatic page breaks and styling

    Example usage:
        generator = PDFReportGenerator()

        # Single company report
        pdf_buffer = generator.generate_single_company_report(
            company_data, metrics, scores
        )

        # Multi-company comparison
        pdf_buffer = generator.generate_comparison_report(
            [company1_data, company2_data, ...]
        )
    """

    # Score level colors for visual feedback
    SCORE_COLORS = {
        "Excellent": colors.HexColor("#059669"),  # Green
        "Good": colors.HexColor("#10b981"),        # Light green
        "Fair": colors.HexColor("#f59e0b"),        # Orange
        "Poor": colors.HexColor("#ef4444"),        # Red
        "Very Poor": colors.HexColor("#dc2626")    # Dark red
    }

    # Category colors
    CATEGORY_COLORS = {
        "Environmental": colors.HexColor("#10b981"),
        "Social": colors.HexColor("#3b82f6"),
        "Governance": colors.HexColor("#8b5cf6")
    }

    def __init__(self):
        """Initialize the PDF Report Generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        logger.info("PDF Report Generator initialized")

    def _setup_custom_styles(self):
        """Create custom paragraph styles for consistent formatting."""

        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor("#059669"),
            spaceAfter=12,
            alignment=TA_CENTER
        ))

        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor("#374151"),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreText',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=6
        ))

    def generate_single_company_report(
        self,
        company: Dict,
        metrics: List[Dict],
        scores: Dict
    ) -> io.BytesIO:
        """
        Generate a detailed PDF report for a single company.

        Args:
            company: Company info dict (name, research_date, etc.)
            metrics: List of 15 sustainability metrics
            scores: Scores dict (final_score, category scores, etc.)

        Returns:
            BytesIO buffer containing the PDF file

        Example:
            pdf_buffer = generator.generate_single_company_report(
                company={"name": "Tesla", "research_date": "2025-01-10"},
                metrics=[{...}, {...}, ...],  # 15 metrics
                scores={"final_score": 78.5, ...}
            )
            # pdf_buffer can be saved to file or sent to user
        """
        logger.info(f"📄 Generating PDF report for: {company['name']}")

        # Create PDF buffer in memory
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build document content
        story = []

        # === COVER PAGE ===
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            "Sustainability Research Report",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.3 * inch))

        # Company name
        story.append(Paragraph(
            company['name'],
            self.styles['CompanyName']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # Overall score with color
        score_level = self._get_score_level(scores['final_score'])
        score_color = self.SCORE_COLORS.get(score_level, colors.black)

        score_text = f"""
        <para align=center>
            <font size=48 color='{score_color.hexval()}'>
                <b>{scores['final_score']:.1f}/100</b>
            </font>
        </para>
        """
        story.append(Paragraph(score_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Rating
        rating_text = f"""
        <para align=center>
            <font size=18 color='{score_color.hexval()}'>
                <b>{score_level}</b>
            </font>
        </para>
        """
        story.append(Paragraph(rating_text, self.styles['Normal']))
        story.append(Spacer(1, 0.5 * inch))

        # Report metadata
        research_date = datetime.fromisoformat(company['research_date']).strftime("%B %d, %Y")
        metadata_text = f"""
        <para align=center>
            <font size=10 color='#6b7280'>
                Analysis Date: {research_date}<br/>
                Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </font>
        </para>
        """
        story.append(Paragraph(metadata_text, self.styles['Normal']))

        # Page break before content
        story.append(PageBreak())

        # === CATEGORY SCORES SECTION ===
        story.append(Paragraph("Category Scores", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2 * inch))

        # Category scores table
        category_data = [
            ['Category', 'Score', 'Weight', 'Rating']
        ]

        categories = [
            ('Environmental', scores.get('environmental_score', 0), '40%'),
            ('Social', scores.get('social_score', 0), '35%'),
            ('Governance', scores.get('governance_score', 0), '25%')
        ]

        for cat_name, cat_score, weight in categories:
            cat_level = self._get_score_level(cat_score)
            category_data.append([
                cat_name,
                f"{cat_score:.1f}",
                weight,
                cat_level
            ])

        category_table = Table(category_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
        category_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#374151")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#d1d5db")),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))

        story.append(category_table)
        story.append(Spacer(1, 0.4 * inch))

        # === DETAILED METRICS SECTION ===
        story.append(Paragraph("Detailed Metrics (All 15)", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2 * inch))

        # Group metrics by category
        metrics_by_category = {}
        for metric in metrics:
            category = metric['category']
            if category not in metrics_by_category:
                metrics_by_category[category] = []
            metrics_by_category[category].append(metric)

        # Display metrics for each category
        for category in ['Environmental', 'Social', 'Governance']:
            if category not in metrics_by_category:
                continue

            # Category header
            cat_color = self.CATEGORY_COLORS.get(category, colors.black)
            story.append(Paragraph(
                f"<font color='{cat_color.hexval()}'><b>{category} Metrics</b></font>",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 0.1 * inch))

            # Metrics table
            metrics_data = [['Metric', 'Value', 'Confidence']]

            for metric in metrics_by_category[category]:
                metrics_data.append([
                    metric['metric_name'],
                    f"{metric['value']:.1f}",
                    f"{metric['confidence']:.0%}"
                ])

            metrics_table = Table(metrics_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), cat_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

                # Data
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))

            story.append(metrics_table)
            story.append(Spacer(1, 0.3 * inch))

        # === FOOTER ===
        story.append(Spacer(1, 0.3 * inch))
        footer_text = """
        <para align=center>
            <font size=8 color='#9ca3af'>
                Generated by Multi-Agent ESG Research System<br/>
                This report is based on publicly available data and AI analysis
            </font>
        </para>
        """
        story.append(Paragraph(footer_text, self.styles['Normal']))

        # Build PDF
        doc.build(story)

        # Reset buffer position
        buffer.seek(0)

        logger.info(f"✅ PDF report generated for {company['name']}")
        return buffer

    def generate_comparison_report(
        self,
        companies_data: List[Dict]
    ) -> io.BytesIO:
        """
        Generate a comparison PDF report for multiple companies.

        Args:
            companies_data: List of dicts, each containing:
                - company: Company info
                - metrics: List of metrics
                - scores: Scores dict

        Returns:
            BytesIO buffer containing the PDF file

        Example:
            companies_data = [
                {
                    "company": {"name": "Tesla", ...},
                    "metrics": [...],
                    "scores": {...}
                },
                {
                    "company": {"name": "Apple", ...},
                    "metrics": [...],
                    "scores": {...}
                }
            ]
            pdf_buffer = generator.generate_comparison_report(companies_data)
        """
        logger.info(f"📊 Generating comparison report for {len(companies_data)} companies")

        # Create PDF buffer
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # === COVER PAGE ===
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            "Sustainability Comparison Report",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.3 * inch))

        # Company names
        company_names = " vs ".join([data['company']['name'] for data in companies_data])
        story.append(Paragraph(
            company_names,
            self.styles['CompanyName']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # Report metadata
        metadata_text = f"""
        <para align=center>
            <font size=10 color='#6b7280'>
                Companies Compared: {len(companies_data)}<br/>
                Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </font>
        </para>
        """
        story.append(Paragraph(metadata_text, self.styles['Normal']))

        story.append(PageBreak())

        # === OVERALL COMPARISON ===
        story.append(Paragraph("Overall Scores Comparison", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2 * inch))

        # Overall scores table
        overall_data = [['Company', 'Final Score', 'Rating', 'Analysis Date']]

        for data in companies_data:
            company = data['company']
            scores = data['scores']
            score_level = self._get_score_level(scores['final_score'])
            research_date = datetime.fromisoformat(company['research_date']).strftime("%b %d, %Y")

            overall_data.append([
                company['name'],
                f"{scores['final_score']:.1f}",
                score_level,
                research_date
            ])

        overall_table = Table(overall_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        overall_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#374151")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Data
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#d1d5db")),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))

        story.append(overall_table)
        story.append(Spacer(1, 0.4 * inch))

        # === CATEGORY COMPARISON ===
        story.append(Paragraph("Category Scores Comparison", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2 * inch))

        # Category comparison table
        category_headers = ['Company', 'Environmental (40%)', 'Social (35%)', 'Governance (25%)']
        category_comp_data = [category_headers]

        for data in companies_data:
            scores = data['scores']
            category_comp_data.append([
                data['company']['name'],
                f"{scores.get('environmental_score', 0):.1f}",
                f"{scores.get('social_score', 0):.1f}",
                f"{scores.get('governance_score', 0):.1f}"
            ])

        category_comp_table = Table(category_comp_data, colWidths=[2*inch, 1.75*inch, 1.75*inch, 1.75*inch])
        category_comp_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#374151")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Data
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#d1d5db")),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))

        story.append(category_comp_table)
        story.append(Spacer(1, 0.4 * inch))

        # === DETAILED METRICS COMPARISON ===
        # For each company, show a section with their metrics
        for data in companies_data:
            story.append(PageBreak())

            company_name = data['company']['name']
            story.append(Paragraph(
                f"Detailed Metrics: {company_name}",
                self.styles['SectionHeading']
            ))
            story.append(Spacer(1, 0.2 * inch))

            # Group metrics by category
            metrics_by_category = {}
            for metric in data['metrics']:
                category = metric['category']
                if category not in metrics_by_category:
                    metrics_by_category[category] = []
                metrics_by_category[category].append(metric)

            # Display metrics for each category
            for category in ['Environmental', 'Social', 'Governance']:
                if category not in metrics_by_category:
                    continue

                cat_color = self.CATEGORY_COLORS.get(category, colors.black)
                story.append(Paragraph(
                    f"<font color='{cat_color.hexval()}'><b>{category}</b></font>",
                    self.styles['Normal']
                ))
                story.append(Spacer(1, 0.1 * inch))

                # Metrics table
                metrics_data = [['Metric', 'Value', 'Confidence']]

                for metric in metrics_by_category[category]:
                    metrics_data.append([
                        metric['metric_name'],
                        f"{metric['value']:.1f}",
                        f"{metric['confidence']:.0%}"
                    ])

                metrics_table = Table(metrics_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), cat_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))

                story.append(metrics_table)
                story.append(Spacer(1, 0.2 * inch))

        # === FOOTER ===
        story.append(Spacer(1, 0.3 * inch))
        footer_text = """
        <para align=center>
            <font size=8 color='#9ca3af'>
                Generated by Multi-Agent ESG Research System<br/>
                This comparison is based on publicly available data and AI analysis
            </font>
        </para>
        """
        story.append(Paragraph(footer_text, self.styles['Normal']))

        # Build PDF
        doc.build(story)

        # Reset buffer position
        buffer.seek(0)

        logger.info(f"✅ Comparison report generated for {len(companies_data)} companies")
        return buffer

    def _get_score_level(self, score: float) -> str:
        """
        Convert numerical score to qualitative rating.

        Args:
            score: Numerical score (0-100)

        Returns:
            Rating string (Excellent, Good, Fair, Poor, Very Poor)
        """
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 30:
            return "Poor"
        else:
            return "Very Poor"


def test_pdf_generator():
    """
    Test the PDF generator with sample data.
    """
    print("=" * 70)
    print("TESTING PDF REPORT GENERATOR")
    print("=" * 70)

    try:
        from database.db_manager import DatabaseManager

        # Initialize
        db = DatabaseManager()
        generator = PDFReportGenerator()

        # Get a company from database (assuming one exists)
        companies = db.get_all_companies()

        if not companies:
            print("⚠️ No companies in database. Run analysis first.")
            return

        # Get first company's data
        company = companies[0]
        company_id = company['id']

        metrics = db.get_metrics(company_id)
        scores = db.get_latest_score(company_id)

        if not metrics or not scores:
            print("⚠️ Incomplete data for company. Run full analysis first.")
            return

        # Generate single company report
        print(f"\nGenerating single company report for: {company['name']}")
        pdf_buffer = generator.generate_single_company_report(company, metrics, scores)

        # Save to file
        filename = f"test_report_{company['name'].replace(' ', '_')}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        print(f"✅ Single company report saved: {filename}")

        # If multiple companies exist, test comparison report
        if len(companies) >= 2:
            print(f"\nGenerating comparison report...")

            companies_data = []
            for comp in companies[:3]:  # Max 3 companies for comparison
                comp_metrics = db.get_metrics(comp['id'])
                comp_scores = db.get_latest_score(comp['id'])

                if comp_metrics and comp_scores:
                    companies_data.append({
                        'company': comp,
                        'metrics': comp_metrics,
                        'scores': comp_scores
                    })

            if len(companies_data) >= 2:
                comparison_buffer = generator.generate_comparison_report(companies_data)

                # Save comparison report
                comp_filename = "test_comparison_report.pdf"
                with open(comp_filename, 'wb') as f:
                    f.write(comparison_buffer.getvalue())

                print(f"✅ Comparison report saved: {comp_filename}")

        print("\n" + "=" * 70)
        print("✅ TEST PASSED: PDF generation successful")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pdf_generator()
