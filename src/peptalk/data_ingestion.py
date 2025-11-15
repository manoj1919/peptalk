# src/peptalk/data_ingestion.py

import requests
from bs4 import BeautifulSoup
import re
import html_to_markdown

MPEP_URLS = [
    'https://www.uspto.gov/web/offices/pac/mpep/s2141.html',
    'https://www.uspto.gov/web/offices/pac/mpep/s2142.html',
    'https://www.uspto.gov/web/offices/pac/mpep/s2143.html',
    'https://www.uspto.gov/web/offices/pac/mpep/s2144.html',
    'https://www.uspto.gov/web/offices/pac/mpep/s2145.html'
]

def scrape_mpep_sections(urls: list, output_file: str) -> bool:
    """
    Scrapes MPEP content from a list of URLs and saves to a single file.
    Returns True on success, False on failure.
    """
    all_text = ""
    print("Starting scraper...")

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- THIS IS THE CORRECTED LINE ---
            # Based on the HTML you provided, 'article' is the correct ID
            content_div = soup.find('div', id='article')
            
            if content_div:
                # Convert the raw HTML of the article to Markdown
                # This preserves headings, lists, bolding, etc.
                html_content = str(content_div)
                markdown_text = html_to_markdown.convert(html_content)

                # Add a clear separator for our splitter
                all_text += f"\n\n# START OF SECTION {url.split('/')[-1]}\n\n"
                all_text += markdown_text
                print(f"Successfully scraped {url}")
            else:
                # This warning will fire if the ID changes again
                print(f"WARNING: Could not find 'id=article' div in {url}")

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not fetch {url}. Error: {e}")
            return False

    try:
        # Note: We're saving this to the 'data/' folder
        output_path = f'data/mpep_2141-2145.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(all_text)
        print(f"\nScraping complete! Data saved to {output_path}")
        return True
    except IOError as e:
        print(f"ERROR: Could not write to file {output_path}. Error: {e}")
        return False

if __name__ == "__main__":
    # We'll run the function to save the file
    scrape_mpep_sections(MPEP_URLS, 'mpep_2141-2145.md')