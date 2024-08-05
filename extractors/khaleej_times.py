import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from datetime import datetime, timedelta
from utils.db_utils import save_article
import logging
from utils.keywords import CREDIT_RATING_KEYWORDS

logging.basicConfig(level=logging.DEBUG)


def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    matched_keywords = [keyword for keyword in CREDIT_RATING_KEYWORDS if keyword.lower() in content]
    return matched_keywords

def fetch_articles_list():
    url = "https://www.khaleejtimes.com/business"
    headers = {
        'Referer': 'https://www.khaleejtimes.com/business',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'incap_ses_772_1773870=4CXHSGNaeTkbA7UsB7K2Cl87n2YAAAAAz2I1asNuV48aKe3ZZEMvCQ==; nlbi_1773870=QYRhZzacMl3AIJY0VzlQLAAAAAC3K7TQ2gLjW1numx77Zk72; visid_incap_1773870=LPw06ZDMS9i/GYLruvNx+5kDeWYAAAAAQUIPAAAAAAD/V6sxJScc4n5qsmVmotvd; boxx_token_id_kt=58426d54b8f6-baaec490a129-445568a8f39e-fa2a04f5af62'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []

    for article in soup.select('div.rendered_board_article'):
        title_tag = article.select_one('h2.post-title a')
        summary_tag = article.select_one('div.entry-summary p.post-summary')
        image_tag = article.select_one('div.post-thumbnail img')

        if title_tag and summary_tag and image_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            summary = summary_tag.get_text(strip=True)
            image_url = image_tag.get('data-srcset', '').split()[0] if image_tag.get('data-srcset') else ''

            articles.append({
                'title': title,
                'link': link,
                'summary': summary,
                'image_url': image_url
            })

    return articles

async def fetch_article_details(session, url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'visid_incap_1773870=jTfFqwH5TOqMe5PeX9zRx/v9RmYAAAAAQUIPAAAAAADfYE/LU8r826cONMMtT0Ut; nlbi_1773870=+tT5GzxuBxVKyavuVzlQLAAAAABrhVI5Hd3cULQ+mv1yKwlm; user_sessions_executed=done; random_user=2; random_user_widget=0; gsi_session=1; boxx_token_id_kt=c3534e13aad0-f7daece888ce-c8795713d1db-df378ae3f390; incap_ses_772_1773870=fQufKtBULAbckbQsB7K2Cto6n2YAAAAA0PHbpXeZyCGyUMltYJxwhw==; adblock_detection=done; user_sessions=2; incap_ses_772_1773870=4CXHSGNaeTkbA7UsB7K2Cl87n2YAAAAAz2I1asNuV48aKe3ZZEMvCQ==; nlbi_1773870=QYRhZzacMl3AIJY0VzlQLAAAAAC3K7TQ2gLjW1numx77Zk72; visid_incap_1773870=LPw06ZDMS9i/GYLruvNx+5kDeWYAAAAAQUIPAAAAAAD/V6sxJScc4n5qsmVmotvd; boxx_token_id_kt=5bfe50acaac3-509d1140c770-c0b0451b9f22-c8a6276dbbe3',
        'priority': 'u=0, i',
        'referer': 'https://www.khaleejtimes.com/business',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')

        # Extract image URL
        image_tag = soup.select_one('div.article-lead-img-pan img')
        image_url = image_tag['srcset'].split()[0] if image_tag and 'srcset' in image_tag.attrs else ''

        # Extract published date
        published_date_tag = soup.select_one('div.article-top-author-nw-nf-right p span')
        published_date = published_date_tag.next_sibling.strip() if published_date_tag else ''

        # Extract full description
        description_tags = soup.select('div.article-nwsplit-arp-wrap-nf p')
        description = "\n".join(tag.get_text(strip=True) for tag in description_tags)

        return {
            'image_url': image_url,
            'published_date': published_date,
            'description': description
        }

def is_recent_date(date_str):
    try:
        article_date = datetime.strptime(date_str, "%a %d %b %Y, %I:%M %p")
        today = datetime.now()
        yesterday = today - timedelta(1)
        return article_date.date() in [today.date(), yesterday.date()]
    except ValueError:
        return False

async def khaleej_times_articles():
    articles = fetch_articles_list()
    detailed_articles = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for article in articles:
            tasks.append(fetch_article_details(session, article['link']))

        details_list = await asyncio.gather(*tasks)

        for article, details in zip(articles, details_list):
            if is_recent_date(details['published_date']):
                matched_keywords = is_credit_rating_related(article['title'], article['summary'])
                if not matched_keywords:
                    logging.debug(f"Skipping non-relevant article: {article['title']}")
                    continue

                article_data = {
                    'title': article['title'],
                    'date': datetime.strptime(details['published_date'], "%a %d %b %Y, %I:%M %p").strftime('%Y-%m-%d'),
                    'summary': article['summary'],
                    'url': article['link'],
                    'source': 'Khaleej Times',
                    'keywords': ', '.join(matched_keywords),
                    'description': details['description']
                }
                save_article(article_data)
                detailed_articles.append(article_data)

    return detailed_articles

def run_khaleej_times_articles():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(khaleej_times_articles())
