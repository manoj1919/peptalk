#
# REPLACE THIS FILE
# File: peptalk/backend/src/peptalk/data_ingestion.py
#
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

def scrape_mpep_sections(urls: list, output_dir: str) -> bool:
    """
    Scrapes MPEP content from a list of URLs and saves each
    to a SEPARATE file in the output directory.
    Returns True on success, False on failure.
    """
    print("Starting scraper...")
    
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_div = soup.find('div', id='article')
            
            if content_div:
                # Convert the raw HTML of the article to Markdown
                html_content = str(content_div)
                markdown_text = html_to_markdown.convert(html_content)
                
                # --- NEW LOGIC ---
                # Generate a clean filename, e.g., "mpep_2141.md"
                section_name = url.split('/')[-1].replace('.html', '').replace('s', 'mpep_')
                output_filename = f"{section_name}.md"
                output_path = f"{output_dir}/{output_filename}"

                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_text)
                    print(f"Successfully scraped and saved to {output_path}")
                except IOError as e:
                    print(f"ERROR: Could not write to file {output_path}. Error: {e}")
                    return False
                # --- END NEW LOGIC ---

            else:
                print(f"WARNING: Could not find 'id=article' div in {url}")

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not fetch {url}. Error: {e}")
            # Continue to the next URL instead of failing entirely
            pass 

    print("\nScraping complete!")
    return True

if __name__ == "__main__":
    # We now pass the *directory* to save files in
    scrape_mpep_sections(MPEP_URLS, 'data')