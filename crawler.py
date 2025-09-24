# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "python-dotenv>=1.0.1",
#     "openai>=1.51.2",
#     "playwright>=1.48.0",
# ]
# ///

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys

from dotenv import load_dotenv
from openai import OpenAI
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    print('❌ OPENAI_API_KEY environment variable is required')
    sys.exit(1)

openai = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# To save on API costs, I've commented out additional sites while you run
# initial tests. Uncomment these sites to do a full run of the news audit.
CHARITY_NEWS_WEBSITES = [
    "https://www.thirdsector.co.uk/news",
    # "https://www.civilsociety.co.uk/",
    # "https://www.charitytoday.co.uk/",
    # "https://www.bbc.co.uk/news/topics/c9z6w63q5elt"
]

async def crawl_all_news_sources():
    print('Starting news crawl...')

    # Create data directory if it doesn't exist
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        all_articles = []

        try:
            for page_url in CHARITY_NEWS_WEBSITES:
                print(f'🔍 Analyzing HTML from: {page_url}')

                try:
                    articles = await extract_articles_from_page(browser, page_url)
                    all_articles.extend(articles)
                except Exception as error:
                    print(f'❌ Failed to analyze {page_url}: {str(error)}')
        finally:
            await browser.close()

    # Save results
    output_path = data_dir / 'crawled-articles.json'
    with open(output_path, 'w') as f:
        json.dump(all_articles, f, indent=2)

    print(f'Crawl complete! Found {len(all_articles)} recent articles.')
    print(f'Results saved to: {output_path}.')

async def extract_articles_from_page(browser, page_url):
    """
    Extract recent articles from a single news source using AI

    Args:
        browser: Playwright browser instance
        page_url (str): URL of the news source

    Returns:
        list: Array of extracted articles from the last 7 days
    """
    page = await browser.new_page()

    try:
        # Navigate to the source page
        await page.goto(page_url, wait_until='networkidle', timeout=30000)

        # Get the HTML content from the <main> section (fallback to body if no main)
        html_content = await page.evaluate("""
            () => {
                const mainElement = document.querySelector('main');
                return mainElement ? mainElement.outerHTML : document.body.innerHTML;
            }
        """)

        # Todo: remove irrelevant tokens from the html_content before analyzing it.

        # Use AI to extract recent articles from HTML
        return await analyze_html_for_recent_articles(html_content, page_url)
    except Exception as error:
        print(f'❌ Failed to extract from {page_url}: {str(error)}')
        return []
    finally:
        await page.close()

async def analyze_html_for_recent_articles(html_content, page_url):
    """
    Use AI to analyze HTML content and extract recent articles

    Args:
        html_content (str): Full HTML content of the page
        page_url (str): URL of the source page

    Returns:
        list: array of recent articles
    """
    current_date = datetime.now().strftime('%Y-%m-%d')  # YYYY-MM-DD format
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    system_prompt = f"""You are a charity sector news analyst. Analyze this HTML content to extract recent news articles.

Today's date is: {current_date}
Only extract articles published within the last 7 days (since {seven_days_ago}).

Look for:
- Article titles and their URLs
- Publication dates (look for dates, timestamps, "posted", "published", etc.)
- Brief descriptions or excerpts
- Focus on charity/nonprofit sector news

Respond with JSON in this exact format:
{{
  "articles": [
    {{
      "url": "full article URL",
      "title": "article title",
      "description": "brief description or excerpt",
      "publishDate": "YYYY-MM-DD or approximate date"
    }}
  ]
}}

Only include articles that are clearly from the last 7 days. If you can't determine the date, include it but mark publishDate as "unknown"."""

    user_prompt = f"""HTML Content:
{html_content[:28000]}..."""

    # Todo: experiment with different models and monitor token input / output usage

    try:
        response = openai.chat.completions.create(
            model='gpt-5-nano',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            response_format={'type': 'json_object'}
        )

        content = response.choices[0].message.content if response.choices else None
        if not content:
            print(f'⚠️ No response from AI for {page_url}')
            return []

        result = json.loads(content)
        articles = result.get('articles', [])

        print(f'📰 Found {len(articles)} recent articles from {page_url}')
        return articles

    except Exception as error:
        print(f'❌ AI analysis failed for {page_url}: {str(error)}')
        return []

if __name__ == '__main__':
    asyncio.run(crawl_all_news_sources())