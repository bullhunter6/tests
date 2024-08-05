import aiohttp
import asyncio
from datetime import datetime
from utils.db_utils import save_article
import logging
from utils.keywords import CREDIT_RATING_KEYWORDS
logging.basicConfig(level=logging.DEBUG)


def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    matched_keywords = [keyword for keyword in CREDIT_RATING_KEYWORDS if keyword.lower() in content]
    return matched_keywords

async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def fetch_recent_stories():
    urls = [
        "https://www.reuters.com/pf/api/v3/content/fetch/recent-stories-by-sections-v1?query=%7B%22section_ids%22%3A%22%2Fbusiness%2F%22%2C%22size%22%3A50%2C%22website%22%3A%22reuters%22%7D&d=204&_website=reuters",
        "https://www.reuters.com/pf/api/v3/content/fetch/articles-by-section-alias-or-id-v1?query=%7B%22arc-site%22%3A%22reuters%22%2C%22fetch_type%22%3A%22collection%22%2C%22id%22%3A%22%2Fbusiness%2F%22%2C%22offset%22%3A20%2C%22section_id%22%3A%22%2Fbusiness%2F%22%2C%22size%22%3A50%2C%22uri%22%3A%22%2Fbusiness%2F%22%2C%22website%22%3A%22reuters%22%7D&d=204&_website=reuters",
        "https://www.reuters.com/pf/api/v3/content/fetch/articles-by-trends-v1?query=%7B%22size%22%3A50%2C%22website%22%3A%22reuters%22%7D&d=204&_website=reuters"
    ]

    headers = {
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-device-memory': '8',
        'Referer': 'https://www.reuters.com/world/middle-east/',
        'sec-ch-ua-full-version-list': '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.127", "Google Chrome";v="126.0.6478.127"',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'reuters-geo={"country":"AE", "region":"-"}'
    }

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, headers) for url in urls]
        responses = await asyncio.gather(*tasks)
    
    articles = []
    unique_ids = set()
    for data in responses:
        if 'result' in data and isinstance(data['result'], dict):
            for article in data['result'].get('articles', []):
                article_id = article.get('id')
                if article_id and article_id not in unique_ids:
                    unique_ids.add(article_id)
                    articles.append(article)

    return articles

async def extract_article_details(article, session, headers):
    details = {
        "ID": article.get("id"),
        "Canonical URL": f"https://www.reuters.com{article.get('canonical_url')}",
        "Title": article.get("title"),
        "Description": article.get("description"),
        "Published Time": article.get("published_time")
    }

    content_url = f"https://www.reuters.com/pf/api/v3/content/fetch/article-by-id-or-url-v1?query=%7B%22published%22%3A%22true%22%2C%22section_optional_fields%22%3A%22all%22%2C%22website%22%3A%22reuters%22%2C%22website_url%22%3A%22{article.get('canonical_url')}%22%7D&d=204&_website=reuters"
    async with session.get(content_url, headers=headers) as response:
        if response.status == 200:
            full_article_data = await response.json()
            if full_article_data.get('result'):
                full_article = full_article_data['result']
                content_elements = full_article.get("content_elements", [])
                if content_elements:
                    details["Content"] = "\n\n".join([elem["content"] for elem in content_elements if elem.get("type") == "paragraph"])
                else:
                    details["Content"] = ""
        else:
            details["Content"] = ""

    return details

async def reuters_articles():
    headers = {
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-device-memory': '8',
        'Referer': 'https://www.reuters.com/world/middle-east/',
        'sec-ch-ua-full-version-list': '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.127", "Google Chrome";v="126.0.6478.127"',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'reuters-geo={"country":"AE", "region":"-"}'
    }

    articles = await fetch_recent_stories()
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = [extract_article_details(article, session, headers) for article in articles]
        details_list = await asyncio.gather(*tasks)

    for details in details_list:
        title = details.get("Title")
        summary = details.get("Description")
        link = details.get("Canonical URL")
        published_time = details.get("Published Time")
        date = datetime.fromisoformat(published_time.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        
        matched_keywords = is_credit_rating_related(title, summary)
        if not matched_keywords:
            logging.debug(f"Skipping non-relevant article: {title}")
            continue

        logging.debug(f"Article found: {title}, {date}, {link}")

        article_data = {
            'title': title,
            'date': date,
            'summary': summary,
            'url': link,
            'source': 'Reuters',
            'keywords': ', '.join(matched_keywords)
        }
        save_article(article_data)
        results.append(article_data)
    
    return results

def run_reuters_articles():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reuters_articles())
