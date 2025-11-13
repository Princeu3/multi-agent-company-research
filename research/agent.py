"""
Research Agent for Company Sustainability Data

This module handles the research phase of sustainability analysis:
1. Searches the web for sustainability information (using Perplexity AI)
2. Scrapes the content from found URLs (using Firecrawl)
3. Returns structured data for analysis

Student Guide:
--------------
- ResearchAgent: Main class that coordinates search and scraping
- search_company(): Finds relevant URLs about a company
- scrape_url(): Gets the actual content from a URL
- research_company(): Puts it all together (search + scrape)
"""

import os
import time
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
import requests

# Load API keys and settings from .env file
load_dotenv()

# Setup logging to track what the agent is doing
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Finds and collects sustainability information about companies.

    Uses two APIs:
    - Perplexity: AI-powered search to find relevant URLs
    - Firecrawl: Web scraper to extract content from URLs

    Example usage:
        agent = ResearchAgent()
        result = agent.research_company("Tesla")
        print(result['sources'])  # List of scraped content
    """

    def __init__(self):
        """
        Initialize the agent with API credentials.

        Raises:
            ValueError: If API keys are missing from environment
        """
        # Get API keys from environment variables
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')

        # Check that we have the required API keys
        if not self.perplexity_api_key:
            raise ValueError("Missing PERPLEXITY_API_KEY in .env file")
        if not self.firecrawl_api_key:
            raise ValueError("Missing FIRECRAWL_API_KEY in .env file")

        # API endpoints (where we send our requests)
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        self.firecrawl_url = "https://api.firecrawl.dev/v1/scrape"

        logger.info("Research Agent initialized successfully")

    def search_company(self, company_name: str) -> List[str]:
        """
        Step 1: Search for sustainability information URLs.

        Uses Perplexity AI to find credible sources about the company's
        environmental, social, and governance (ESG) practices.

        Args:
            company_name: Name of the company (e.g., "Tesla", "Apple")

        Returns:
            List of URLs (up to 10) that contain sustainability information

        Example:
            urls = agent.search_company("Tesla")
            # Returns: ["https://tesla.com/impact", "https://...", ...]
        """
        logger.info(f"🔍 Searching for: {company_name}")

        # Prepare the API request headers
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }

        # Create a detailed search query focusing on sustainability
        query = f"""Find recent and credible sources about {company_name}'s sustainability practices.

        Topics to focus on:
        - Environmental: carbon emissions, renewable energy, waste management
        - Social: labor practices, diversity, community impact
        - Governance: ethics, transparency, board structure

        Provide URLs to official reports, news articles, and credible sources."""

        # Prepare the API request body
        payload = {
            "model": "sonar",  # Perplexity's search model
            "messages": [
                {
                    "role": "system",
                    "content": "You are a sustainability research assistant. Provide credible sources with URLs."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.2,  # Low temperature = more focused results
            "max_tokens": 1000
        }

        try:
            # Send the search request to Perplexity API
            response = requests.post(
                self.perplexity_url,
                json=payload,
                headers=headers,
                timeout=30  # Wait max 30 seconds for response
            )
            response.raise_for_status()  # Raise error if request failed

            # Parse the JSON response
            data = response.json()

            # Extract URLs from the citations field
            # Citations are the sources Perplexity found
            urls = []
            if 'citations' in data:
                urls = data['citations'][:10]  # Take top 10 sources

            logger.info(f"✓ Found {len(urls)} sources for {company_name}")
            return urls

        except requests.exceptions.RequestException as e:
            # If the request fails, log the error and return empty list
            logger.error(f"❌ Search failed: {str(e)}")
            return []

    def scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Step 2: Extract content from a single URL.

        Uses Firecrawl API to scrape the webpage and convert it to
        clean markdown text that's easy to analyze.

        Args:
            url: The webpage URL to scrape

        Returns:
            Dictionary with 'url' and 'content' keys if successful
            None if scraping fails

        Example:
            result = agent.scrape_url("https://tesla.com/impact")
            # Returns: {"url": "...", "content": "Tesla's sustainability..."}
        """
        logger.info(f"📄 Scraping: {url}")

        # Prepare the API request headers
        headers = {
            "Authorization": f"Bearer {self.firecrawl_api_key}",
            "Content-Type": "application/json"
        }

        # Configure the scraping options
        payload = {
            "url": url,
            "formats": ["markdown"],  # Get content as markdown (clean text)
            "onlyMainContent": True,   # Skip headers, footers, ads
            "waitFor": 1000            # Wait 1 second for page to load
        }

        try:
            # Send the scrape request to Firecrawl API
            response = requests.post(
                self.firecrawl_url,
                json=payload,
                headers=headers,
                timeout=45  # Scraping takes longer, wait up to 45 seconds
            )
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Check if scraping was successful and extract content
            if data.get('success') and 'data' in data:
                content = data['data'].get('markdown', '')

                if content:
                    # Limit content to 50,000 characters to avoid overwhelming the system
                    content = content[:50000]
                    logger.info(f"✓ Scraped {len(content)} characters")

                    return {
                        'url': url,
                        'content': content
                    }

            # If we got here, scraping didn't return useful content
            logger.warning(f"⚠️ No content found at {url}")
            return None

        except requests.exceptions.RequestException as e:
            # If scraping fails, log the error and return None
            logger.error(f"❌ Scraping failed for {url}: {str(e)}")
            return None

    def scrape_sources(self, urls: List[str], max_sources: int = 5) -> List[Dict[str, str]]:
        """
        Step 3: Scrape multiple URLs with smart error handling.

        Tries to scrape up to max_sources successfully. If some URLs fail,
        it tries additional URLs from the list until we have enough sources.

        Args:
            urls: List of URLs to try scraping
            max_sources: How many successful scrapes we want (default: 5)

        Returns:
            List of successfully scraped sources (each with 'url' and 'content')

        Example:
            sources = agent.scrape_sources(url_list, max_sources=5)
            # Returns: [{"url": "...", "content": "..."}, {...}, ...]
        """
        sources = []

        # Try scraping URLs until we have enough sources
        # We try extra URLs (max_sources * 2) in case some fail
        for i, url in enumerate(urls[:max_sources * 2]):
            # Stop if we already have enough sources
            if len(sources) >= max_sources:
                break

            # Try to scrape this URL
            source = self.scrape_url(url)
            if source:
                sources.append(source)

            # Rate limiting: pause between requests to be polite to servers
            if i < len(urls) - 1:
                time.sleep(1.5)  # Wait 1.5 seconds between requests

        logger.info(f"✓ Successfully scraped {len(sources)} sources")
        return sources

    def research_company(self, company_name: str) -> Dict:
        """
        Complete research pipeline: search → scrape → return data.

        This is the main method you'll call. It coordinates the entire
        research process:
        1. Searches for relevant URLs about the company
        2. Scrapes content from those URLs
        3. Returns all the collected information

        Args:
            company_name: Name of the company to research

        Returns:
            Dictionary with structure:
            {
                "company": "Tesla",
                "sources": [
                    {"url": "...", "content": "..."},
                    {"url": "...", "content": "..."},
                    ...
                ]
            }

        Example:
            agent = ResearchAgent()
            data = agent.research_company("Tesla")
            print(f"Found {len(data['sources'])} sources")
            print(data['sources'][0]['content'][:100])  # Preview first source
        """
        logger.info(f"🚀 Starting research for: {company_name}")

        # STEP 1: Find relevant URLs using Perplexity search
        urls = self.search_company(company_name)

        # If search failed, return empty result
        if not urls:
            logger.error(f"❌ No sources found for {company_name}")
            return {
                "company": company_name,
                "sources": []
            }

        # STEP 2: Scrape content from the found URLs
        sources = self.scrape_sources(urls, max_sources=5)

        # Warn if we didn't get many sources
        if len(sources) < 3:
            logger.warning(f"⚠️ Only found {len(sources)} sources (target is 5+)")

        # STEP 3: Package and return the results
        result = {
            "company": company_name,
            "sources": sources
        }

        logger.info(f"✅ Research complete: {len(sources)} sources collected")
        return result


def test_research_agent():
    """
    Test function to verify the Research Agent works correctly.

    This function:
    1. Creates a ResearchAgent instance
    2. Researches "Tesla" as a test case
    3. Prints the results
    4. Checks if we got enough sources
    """
    print("=" * 70)
    print("TESTING RESEARCH AGENT")
    print("=" * 70)
    print("\nSearching for Tesla's sustainability information...\n")

    try:
        # Create the agent
        agent = ResearchAgent()

        # Run the research
        result = agent.research_company("Tesla")

        # Display results
        print(f"Company: {result['company']}")
        print(f"Sources found: {len(result['sources'])}")
        print("\n" + "=" * 70)
        print("SOURCE DETAILS")
        print("=" * 70)

        for i, source in enumerate(result['sources'], 1):
            print(f"\n{i}. URL: {source['url']}")
            print(f"   Content length: {len(source['content'])} characters")
            print(f"   Preview: {source['content'][:150]}...")

        # Check if test passed
        print("\n" + "=" * 70)
        if len(result['sources']) >= 5:
            print("✅ TEST PASSED: Found 5+ sources with content")
        else:
            print(f"⚠️ TEST WARNING: Only found {len(result['sources'])} sources (target is 5+)")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


# When this file is run directly (not imported), run the test
if __name__ == "__main__":
    test_research_agent()
