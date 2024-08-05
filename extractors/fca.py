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

def fca_articles():
    url = "https://www.fca.org.uk/news/rss.xml"
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
        date_text = item.find('pubDate').text.strip()
        summary = item.find('description').text.strip()
        url = item.find('link').text.strip()
        
        matched_keywords = is_credit_rating_related(title, summary)
        if not matched_keywords:
            logging.debug(f"Skipping non-relevant article: {title}")
            continue

        try:
            parsed_date = datetime.strptime(date_text, "%a, %d %b %Y %H:%M:%S %z").strftime('%Y-%m-%d')
            logging.debug(f"Parsed date: {parsed_date} for article: {title}")
        except ValueError:
            logging.error(f"Invalid date format for article: {title} with date: {date_text}")
            continue  # Skip this article if date parsing fails

        article_data = {
            'title': title,
            'date': parsed_date,
            'summary': summary,
            'url': url,
            'source': 'FCA',
            'keywords': ', '.join(matched_keywords)
        }
        save_article(article_data)
        logging.debug(f"Saved article to database: {title}")
        results.append(article_data)
    
    return results
