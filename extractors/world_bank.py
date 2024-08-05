import requests
from bs4 import BeautifulSoup
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

def world_bank_articles():
    url = "https://search.worldbank.org/api/v2/news?format=json&rows=30&fct=displayconttype_exact,topic_exact,lang_exact,count_exact,countcode_exact,admreg_exact&src=cq55&apilang=en&lang_exact=English&&os=0"

    payload = {}
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-length': '0',
        'content-type': 'text/plain',
        'origin': 'https://www.worldbank.org',
        'priority': 'u=1, i',
        'referer': 'https://www.worldbank.org/',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Cookie': '__cf_bm=tI7hcZeOxya3jFB7qEpO_uj4f9tZx.yNthaw6CoDv6Q-1722319865-1.0.1.1-6aVbcqeiD_6VhVVyNPlRHwExftLlaab1Tyn8ezmCHoaDExebTPzJhCdbvqvGJUYhRizu1HVEbicy0Nq_UW4PuA; search.ApplicationGatewayAffinity=fb51af8e6aa3233ad17b87332ccf2d86; search.ApplicationGatewayAffinityCORS=fb51af8e6aa3233ad17b87332ccf2d86'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    articles_data = response_json.get('documents', {}).values()

    results = []

    for article in articles_data:
        title = article.get('title', {}).get('cdata!', 'No title')
        url = article.get('url', 'No URL')
        date = article.get('lnchdt', 'No date')
        if date != 'No date':
            date = date.split('T')[0]
        summary_data = article.get('content', {}).get('cdata!', 'No summary')
        summary = clean_summary(summary_data)
        matched_keywords = is_credit_rating_related(title, summary_data)
        if not matched_keywords:
            logging.debug(f"Skipping non-relevant article: {title}")
            continue


        article_data = {
            'title': title,
            'date': date,
            'summary': summary,
            'url': url,
            'source': 'World Bank',
            'keywords': ', '.join(matched_keywords)
        }
        save_article(article_data)
        logging.debug(f"Saved article to database: {title}")
        results.append(article_data)
    
    return results



def main():
    articles = world_bank_articles()
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Date: {article['date']}")
        print(f"Summary: {article['summary']}\n")
        print(f"Source: {article['source']}")


if __name__ == "__main__":
    main()
