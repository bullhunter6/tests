import requests
from bs4 import BeautifulSoup
import re
from utils.db_utils import save_article
import logging
from utils.keywords import CREDIT_RATING_KEYWORDS

logging.basicConfig(level=logging.DEBUG)



def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    matched_keywords = [keyword for keyword in CREDIT_RATING_KEYWORDS if keyword.lower() in content]
    return matched_keywords

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_summary(html_summary):
    soup = BeautifulSoup(html_summary, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text[:200] + '...' if len(text) > 200 else text

def get_full_summary(link):
    url = f"https://pressroom.ifc.org/all/pages/{link}"

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'pressroom.ApplicationGatewayAffinityCORS=c8f5d878a20c13676d15fa2ddd455ca6; pressroom.ApplicationGatewayAffinity=c8f5d878a20c13676d15fa2ddd455ca6; TS019865bf=0114ae2926fd68ec6e4b7a27a615634c6d3192741c2e5e42f48d67881f25b1e46a75eb4fc6d3261231a80a17722e80d71721732fad',
        'priority': 'u=0, i',
        'referer': 'https://pressroom.ifc.org/all/pages/PressReleaseAll.aspx?language=English',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    summary_div = soup.find('span', id='spancontent')
    
    article_summary = "Summary not found."
    if summary_div:
        raw_text = summary_div.get_text(separator=' ')
        article_summary = clean_text(raw_text)

    return article_summary

def ifc_articles():
    url = "https://pressroom.ifc.org/all/pages/PressReleaseAll.aspx?language=English"

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'pressroom.ApplicationGatewayAffinityCORS=c8f5d878a20c13676d15fa2ddd455ca6; pressroom.ApplicationGatewayAffinity=c8f5d878a20c13676d15fa2ddd455ca6; TS019865bf=0114ae2926b28c250e11088dcb7d0f19dc59c3cf5402039e2e5bf892370efb8b1a5068c9b0b07724c9acc48cd03fa009c1ec24f719',
        'priority': 'u=0, i',
        'referer': 'https://pressroom.ifc.org/all/pages/PressReleaseAll.aspx',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    month_mapping = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
        'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }

    base_url = "https://pressroom.ifc.org/all/pages/"

    pr_data_list = soup.find('div', class_='pr-data-list')
    articles = []
    if pr_data_list:
        press_releases = pr_data_list.find_all('div', class_='pressroom-language-bar')
        for release in press_releases:
            title_tag = release.find('h3', class_='title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.find('a')['href']
                full_link = base_url + link
                date_span = release.find('span', class_='date bubble')
                if date_span:
                    date_parts = [part.strip() for part in date_span.stripped_strings]
                    if len(date_parts) >= 3:
                        day = date_parts[0]
                        month_abbr = date_parts[2]
                        year = date_parts[4]
                        month = month_mapping.get(month_abbr, '01')
                        date = f"{year}-{month}-{day}"
                    else:
                        date = "Date not found"

                full_summary = get_full_summary(link)
                summary = clean_summary(full_summary)

                matched_keywords = is_credit_rating_related(title, full_summary)
                if not matched_keywords:
                    logging.debug(f"Skipping non-relevant article: {title}")
                    continue

                articles.append({
                    'title': title,
                    'url': full_link,
                    'date': date,
                    'summary': summary,
                    'source': 'IFC',
                    'keywords': ', '.join(matched_keywords)
                })

                # Save each article individually
                save_article({
                    'title': title,
                    'url': full_link,
                    'date': date,
                    'summary': summary,
                    'source': 'IFC',
                    'keywords': ', '.join(matched_keywords)
                })
                logging.debug(f"Saved article to database: {title}")

    return articles
