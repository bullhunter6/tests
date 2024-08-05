import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.db_utils import save_article
import logging
from utils.keywords import CREDIT_RATING_KEYWORDS

logging.basicConfig(level=logging.DEBUG)

base_url = "https://www.weforum.org"
press_url = f"{base_url}/press/"

payload = {}
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '_vwo_uuid_v2=DEA9491D2F08C76FDFE2103CFF7781B07|6365a5eb5e42626f0f694824ef419397; _vis_opt_s=1%7C; _vis_opt_test_cookie=1; _vwo_uuid=DEA9491D2F08C76FDFE2103CFF7781B07; CookieConsent={stamp:%27Txdp5ig8ZMy0Kg+Tde/XxCFAj9ismpyzn17ggEk5RrQiiy6bxMkSQQ==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1721194160684%2Cregion:%27ae%27}; _gcl_au=1.1.1446335809.1721194161; _gid=GA1.2.885346948.1721194161; _gat_UA-15704185-3=1; gtm_session_start=1721194166458; _web_session=T3lSUGF0em9KL0wxbWVxZFhIM2FIaWk5bGZXL25FcnlORjBGNFBIczRCNzZNQUlxOGRodkNRMG1TbVRRa2J4dmxNcXhaZ3cvZnFzZGxCZjl3UXYzd2s3MU9rUnlQU1R2TXJpWC93OWdlQ1M1byt0MkpEWmM1Z3J6ZGlJblFKbjF4M0RwSVNOZ3YrdlczbDk5b3lhbDh3PT0tLXo2eFFaTVRIZU1EMkZrUlJ0ZmRGQnc9PQ%3D%3D--fa96ad3a940e14034e54da8e84f77c78de787de2; mpDistinctId=f5deab79-f3c1-481f-b8a0-23e925a1a541; _ga_1RV0X04XBG=GS1.1.1721194158.1.1.1721194188.0.0.0; _ga_2K5FR2KRN5=GS1.1.1721194158.1.1.1721194188.32.0.0; _vwo_sn=0%3A3; _vwo_ds=3%3Aa_0%2Ct_0%3A0%241721194156%3A6.15322432%3A%3A109_0%2C26_0%3A4_0%2C3_0%3A0; _ga_4DKG1LX6QK=GS1.1.1721194158.1.1.1721194188.32.0.0; mp_6232aeb08818ee1161204a011ed8ad16_mixpanel=%7B%22distinct_id%22%3A%20%22f5deab79-f3c1-481f-b8a0-23e925a1a541%22%2C%22%24device_id%22%3A%20%22190bf2a9ff0eff-0d0af64e297c1-26001f51-1bcab9-190bf2a9ff0eff%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22f5deab79-f3c1-481f-b8a0-23e925a1a541%22%2C%22platform%22%3A%20%22Public%20Site%22%7D; _ga=GA1.2.825686345.1721194158; _web_session=clhrSzkxMTNCaEtiRFBHV3lCRk8rdkR5NmVNbmliNHdTc1NPb1NuRE12UTNNUmE2R0pmZi9QMlJzMnBwODZFb093ODdkNnVjMldNTnJSaS8wWEFnajl0MFdmbE00WDZEM2pjOVZ1U0JBOHgzaVNnWVB1LzY4YUU5aGdUaEkrWUJQVGpaUURHeFQxWS8yUWJiakdqU3lnPT0tLUFFdDhpWVVuL0YycThPbWlDQnVyTUE9PQ%3D%3D--e58fd5adf31ff7229913e02b2beb71b42ccaf466',
    'If-None-Match': 'W/"fff0811117294547e38f399dddbd6a32"',
    'Referer': 'https://www.weforum.org/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}


def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    matched_keywords = [keyword for keyword in CREDIT_RATING_KEYWORDS if keyword.lower() in content]
    return matched_keywords

def wef_articles():
    response = requests.get(press_url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('div', class_='media-article')
    results = []

    for article in articles:
        title_link = article.find('a', class_='media-article__link')
        metadata = article.find('div', class_='media-article__metadata')
        if title_link and metadata:
            title = title_link.get_text(strip=True)
            link = base_url + title_link['href']
            news_type = metadata.find('span', class_='caption bold').get_text(strip=True)
            date_text = metadata.find_all('span', class_='caption')[1].get_text(strip=True)
            date = datetime.strptime(date_text, "%d %b %Y").strftime('%Y-%m-%d')

            matched_keywords = is_credit_rating_related(title, news_type)
            if not matched_keywords:
                logging.debug(f"Skipping non-relevant article: {title}")
                continue

            logging.debug(f"Article found: {title}, {date}, {link}")

            article_data = {
                'title': title,
                'date': date,
                'summary': news_type,
                'url': link,
                'source': 'World Economic Forum',
                'keywords': ', '.join(matched_keywords)
            }
            save_article(article_data)
            results.append(article_data)
    
    return results