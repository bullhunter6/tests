import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.db_utils import save_article
import logging
from utils.keywords import CREDIT_RATING_KEYWORDS

logging.basicConfig(level=logging.DEBUG)


def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    matched_keywords = [keyword for keyword in CREDIT_RATING_KEYWORDS if keyword.lower() in content]
    return matched_keywords

def clean_summary(html_summary):
    # Use BeautifulSoup to clean and extract plain text
    soup = BeautifulSoup(html_summary, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    # Limit the summary length to 200 characters
    return text[:200] + '...' if len(text) > 200 else text

def sca_articles():
    url = "https://www.sca.gov.ae/RSS/News.ashx?lang=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'xml')  # Use 'xml' parser
    items = soup.find_all('item')
    
    results = []
    for item in items:
        title = item.find('title').text.strip()
        date = item.find('pubDate').text.strip()
        summary_html = item.find('description').text.strip()
        summary = clean_summary(summary_html)
        url = item.find('link').text.strip()
        
        if not is_credit_rating_related(title, summary):
            logging.debug(f"Skipping non-relevant article: {title}")
            continue

        try:
            parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z").strftime('%Y-%m-%d')
            logging.debug(f"Parsed date: {parsed_date} for article: {title}")
        except ValueError:
            logging.warning(f"Could not parse date: {date} for article: {title}")
            continue
        
        article_data = {
            'title': title,
            'date': parsed_date,
            'summary': summary,
            'url': url,
            'source': 'SCA',
            'keywords': ', '.join(is_credit_rating_related(title, summary))
        }
        save_article(article_data)
        logging.debug(f"Saved article to database: {title}")
        results.append(article_data)
    
    return results

def run_sca_articles():
    sca_articles()
