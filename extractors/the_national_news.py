import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from utils.db_utils import save_article
import logging
import aiohttp
import asyncio
from utils.keywords import CREDIT_RATING_KEYWORDS

logging.basicConfig(level=logging.DEBUG)


def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    matched_keywords = [keyword for keyword in CREDIT_RATING_KEYWORDS if keyword.lower() in content]
    return matched_keywords

async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def fetch_article_details(session, url, headers):
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        script_tags = soup.find_all('script', type='application/ld+json')

        article_data = None
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'NewsArticle':
                    article_data = data
                    break
            except json.JSONDecodeError:
                continue

        return article_data

async def the_national_news_articles():
    url = "https://www.thenationalnews.com/pf/api/v3/content/fetch/clavis-api?query=%7B%22feedOffset%22%3A0%2C%22feedSize%22%3A16%2C%22from%22%3A0%2C%22offset%22%3A0%2C%22section%22%3A%22%2Fbusiness%22%2C%22size%22%3A16%7D&d=756&_website=the-national"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'arc-geo={"country_code":"AE","city":"DUBAI","longitude":"55.28","latitude":"25.25"}; OptanonAlertBoxClosed=2024-07-23T06:10:42.312Z; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jul+23+2024+11%3A13%3A53+GMT%2B0400+(Gulf+Standard+Time)&version=202406.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=22c0fc02-0652-4a4d-9842-cbb05da5230c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1&intType=1&geolocation=AE%3BDU&AwaitingReconsent=false; arc-geo={"country_code":"AE","city":"DUBAI","longitude":"55.28","latitude":"25.25"}',
        'if-modified-since': '1721714355525',
        'priority': 'u=1, i',
        'referer': 'https://www.thenationalnews.com/business/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url, headers)
        articles = response.get("content_elements", [])

        detailed_articles = []
        for article in articles:
            headline = article.get("headlines", {}).get("basic", "No headline")
            summary = article.get("description", "No summary")
            publish_date = article.get("display_date", "No date")
            canonical_url = article.get("canonical_url", "No URL")
            if not canonical_url.startswith("http"):
                article_url = f"https://www.thenationalnews.com{canonical_url}"
            else:
                article_url = canonical_url

            article_data = await fetch_article_details(session, article_url, headers)
            if article_data:
                matched_keywords = is_credit_rating_related(headline, summary)
                if not matched_keywords:
                    logging.debug(f"Skipping non-relevant article: {headline}")
                    continue

                published_time = article_data.get('datePublished', publish_date)
                date = datetime.fromisoformat(published_time.replace('Z', '+00:00')).strftime('%Y-%m-%d')

                article_record = {
                    'title': headline,
                    'date': date,
                    'summary': summary,
                    'url': article_url,
                    'source': 'The National News',
                    'keywords': ', '.join(matched_keywords)
                }
                save_article(article_record)
                detailed_articles.append(article_record)

        return detailed_articles

def run_the_national_news_articles():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(the_national_news_articles())
