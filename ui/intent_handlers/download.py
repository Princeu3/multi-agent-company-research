"""
Download Intent Handler

Handles download-related intents:
- download: Generate and download PDF report for one or more companies

Student Guide:
--------------
This handler:
1. Fetches company data from the database
2. Generates a professional PDF report using ReportLab
3. Provides a download button in the chat interface

Supports:
- Single company reports
- Multi-company comparison reports
"""

import streamlit as st
from typing import List
from datetime import datetime
from ui.components.sidebar import get_companies_from_db
from reports.pdf_generator import PDFReportGenerator


def handle_download(companies: List[str]):
    """
    Handle download intent - generate and provide PDF report.

    Args:
        companies: List of company names to include in the report

    Example:
        handle_download(["Tesla"])
        # Generates single company report

        handle_download(["Tesla", "Apple"])
        # Generates comparison report
    """
    if not companies:
        response = "Please specify which company/companies to download a report for."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    # Get all companies from database
    companies_data_dict = get_companies_from_db()

    # Check if all requested companies are available
    missing_companies = [c for c in companies if c not in companies_data_dict]

    if missing_companies:
        missing_names = ", ".join(missing_companies)
        response = f"I haven't analyzed the following companies yet: {missing_names}\n\n"
        response += "Please analyze them first before downloading a report."
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
        return

    # Initialize PDF generator
    generator = PDFReportGenerator()

    try:
        if len(companies) == 1:
            # Single company report
            company_name = companies[0]
            data = companies_data_dict[company_name]

            response = f"📄 Generating PDF report for **{company_name}**..."
            st.session_state.chat_messages.append({"role": "assistant", "content": response})

            # Generate PDF
            pdf_buffer = generator.generate_single_company_report(
                company=data['company'],
                metrics=data['metrics'],
                scores=data['scores']
            )

            # Create filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{company_name.replace(' ', '_')}_Sustainability_Report_{date_str}.pdf"

            # Add download button to chat
            # Note: We'll store the PDF buffer in session state and create button in main app
            st.session_state.pending_download = {
                'buffer': pdf_buffer,
                'filename': filename,
                'type': 'single'
            }

            success_msg = f"✅ Report ready! Click the button below to download the PDF report for **{company_name}**."
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": success_msg,
                "download": True  # Flag to indicate download button needed
            })

        else:
            # Multi-company comparison report
            company_names = ", ".join(companies)
            response = f"📊 Generating comparison report for **{company_names}**..."
            st.session_state.chat_messages.append({"role": "assistant", "content": response})

            # Prepare data for comparison
            companies_data_list = []
            for company_name in companies:
                data = companies_data_dict[company_name]
                companies_data_list.append({
                    'company': data['company'],
                    'metrics': data['metrics'],
                    'scores': data['scores']
                })

            # Generate comparison PDF
            pdf_buffer = generator.generate_comparison_report(companies_data_list)

            # Create filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            companies_slug = "_vs_".join([c.replace(' ', '_') for c in companies])
            filename = f"Comparison_{companies_slug}_{date_str}.pdf"

            # Store for download
            st.session_state.pending_download = {
                'buffer': pdf_buffer,
                'filename': filename,
                'type': 'comparison'
            }

            success_msg = f"✅ Comparison report ready! Click the button below to download the PDF comparing **{company_names}**."
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": success_msg,
                "download": True  # Flag to indicate download button needed
            })

        st.rerun()

    except Exception as e:
        error_msg = f"❌ Sorry, there was an error generating the PDF report: {str(e)}"
        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        st.rerun()
