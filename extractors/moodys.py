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

def moodys_articles():
    url = "https://www.moodys.com/web/en/us/insights/all/jcr:content/root/container/container_25347621/filter_container_cop.result-set.html?p=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('div', class_='card-insight')

    results = []
    for article in articles:
        title = article.find('h5').text.strip()
        
        date_span = article.find('span', class_='card-date')
        if date_span:
            date_text = date_span.text.strip()
        else:
            logging.debug(f"Skipping article without date: {title}")
            continue
        
        summary_div = article.find('div', class_='card-body')
        if summary_div:
            summary = summary_div.text.strip()
        else:
            logging.debug(f"Skipping article without summary: {title}")
            continue

        relative_url = article.find('a', class_='btn-quick-link')['href']
        full_url = requests.compat.urljoin(url, relative_url)
        
        matched_keywords = is_credit_rating_related(title, summary)
        if not matched_keywords:
            logging.debug(f"Skipping non-relevant article: {title}")
            continue

        try:
            parsed_date = datetime.strptime(date_text, "%b %d, %Y").strftime('%Y-%m-%d')
            logging.debug(f"Parsed date: {parsed_date} for article: {title}")
        except ValueError:
            logging.error(f"Invalid date format for article: {title} with date: {date_text}")
            continue  # Skip this article if date parsing fails

        article_data = {
            'title': title,
            'date': parsed_date,
            'summary': summary,
            'url': full_url,
            'source': 'Moody\'s',
            'keywords': ', '.join(matched_keywords)
        }
        save_article(article_data)
        logging.debug(f"Saved article to database: {title}")
        results.append(article_data)
    
    return results


