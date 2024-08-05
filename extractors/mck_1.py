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

async def fetch(session, url, headers, method='GET', data=None):
    if method == 'POST':
        async with session.post(url, headers=headers, data=data) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch URL: {url} with status code {response.status}")
                return None

            content_type = response.headers.get('Content-Type', '')
            if content_type.startswith('application/json'):
                return await response.json()
            else:
                logging.error(f"Unexpected content type: {content_type} for URL: {url}")
                return None
    else:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch URL: {url} with status code {response.status}")
                return None

            content_type = response.headers.get('Content-Type', '')
            if content_type.startswith('application/json'):
                return await response.json()
            else:
                logging.error(f"Unexpected content type: {content_type} for URL: {url}")
                return None

async def fetch_article_details(session, url, headers):
    try:
        logging.debug(f"Fetching details from URL: {url}")
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch URL: {url} with status code {response.status}")
                return None

            html = await response.text()
            logging.debug(f"Received HTML from {url}")
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
    except Exception as e:
        logging.error(f"Exception occurred while fetching article details: {e}")
        return None


async def mckinsey_articles():
    url = "https://prd-api.mckinsey.com/api/insightsgrid/articles"
    payload = json.dumps({
        "limit": 20,
        "afterId": "",
        "taxonomyAndTags": {
            "taxonomyQueryType": "OR",
            "taxonomyIds": [
                "91cfe105-8dad-437c-8734-3d740dcdb437",
                "0abbc29e-46ee-470b-a93b-c31f735e753a",
                "15750f40-c2b7-4634-be10-763112fad183",
                "21dc6bd4-9b9a-4de0-a9b8-71f68efef898",
                "874ee345-9fa7-403b-bcf3-2eaf719a89fa",
                "1ea27058-9b4d-4a64-81f4-f56cb6b81896",
                "aaf8b700-2f9c-40e9-8037-7a90ebf4e651",
                "fcb448f9-af05-4682-a070-ffab859ebdb5",
                "c3f331dd-6683-4c33-9460-e56bb1487f33",
                "899ef466-0f6e-4feb-965d-3882b88ac9a4",
                "13f7e352-920f-4dd2-9a31-f2c3314eb405",
                "fa4bb8d5-ea76-4dd9-9530-2c865a87d5e0",
                "5b69151c-e124-4dcf-b9e7-212b7320050d",
                "83cf99bc-d256-4e4c-a1bf-d0698ec601e9",
                "a9103a6d-6663-4a30-bf78-9927d74f5df5"
            ],
            "mustHaveTagsQueryType": "OR",
            "mustHaveTags": [
                "8b55ff3d-e6b3-4cc9-8fcd-b817f242672f"
            ],
            "mustNotHaveTagsQueryType": "OR",
            "mustNotHaveTags": [
                "a65a9603-c09a-489f-9d77-4afd71c629b3"
            ]
        },
        "excludeItems": [
            "4a78de41-0ee0-43be-bda4-d644a90b57dc",
            "cd50dd50-ea64-4b47-b9c3-a21a80331630",
            "7b3d4c0a-99f3-4755-be50-322acecea949",
            "733892de-d5ea-477e-994e-1c3c50772e80",
            "15284026-c315-4ccc-9af8-b561b17bcc21",
            "932865d5-c29c-45b5-a1b7-4828f088f7c2",
            "52d53345-1331-41d7-b77b-d55e838766dc",
            "6cf40d71-04fc-43c3-8a6b-9a26be027e92",
            "ed23aa98-ec33-4119-823a-9bb681a4e445",
            "aa0e705f-2850-4bb8-ace3-51d6cf0029fe"
        ],
        "language": "en",
        "isAlumni": False,
        "filters": []
    })

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.mckinsey.com',
        'priority': 'u=1, i',
        'referer': 'https://www.mckinsey.com/featured-insights/future-of-asia/overview',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Cookie': '_abck=54FC7AD8FC8801E4B69A2A1F460EC1DA~-1~YAAQBvttaEPn0cOQAQAAFer+/Ax50rtX9HrYFO5YNpE8b1KfZEXNVRcRiyMEoexMBs2SVft3+sHEismHpEgJeNeV2CsJz48QBB0FVv9kEEAZjNsYdRGN6L2PTxp0UOy6g8WsPkGWY0FrIO8tQiextwbSDwkq3XHEWAKes3JMZBb8NIARM7LwRtMn8NK0cBpqX7ljIShml0JX90vDMfZ9qbXozpWu/kzyl7eV8aAne9aZH/abD0iBOvhF9g36IatG5WGO7oOIRT7mjOqnlpn2v81N6j0L7MvrotNsxxm0jn1al5tXj2RlrVQHKZ2QDTTlz8/K5NvWz/ESNe95X+JgYgV9D31etBXe7AFxooN6lPgPUY9gaQaCJCqeNMyHXhlFBCOAuz6iLHWgojzk~-1~-1~-1; ak_bmsc=6A3354FF281592C737B83F86EDDF4D18~000000000000000000000000000000~YAAQBvttaETn0cOQAQAAFer+/BgwgWwAz7YJHPszVi7kuATALERqjrP+jCs3eJtJ9ACmj0dDQLW/CInMbw9La8oO+Z7XGHnSeKOpLXmrAg4syhqYlFVP4r/HDCZjYfOVzN8FIsXQnohnOgF5IzdJeuB1Ngxj1g7mskj9R5pmbLN8/DNNb8q8drfHI+cyDPDy1EhKJKqJjilsx4PHvDlRRr/lqpomZ+pxjUtebwVS2AecavLafR4eCBCX4J7IuX5g/ZK0pFuNhu6QRQKQflOfOjQiqIXjH+TODr4TKPubi82EgFlaFADdT8/W6DcAuu2HKB6rF9TkFRStvcXsDWZJ2fuG+5kb2PPNXc0waokKI2zUXedDTiTxo0ySXrzH; bm_sz=C41BC5DEEE193AAA48D7F07F2FD4DD72~YAAQBvttaEXn0cOQAQAAFer+/Bj6PRO2/gCtexo00P/a39G+oDdRgpujjrOz/Kn3hGZvXzdVid8QGZZUGdztp3YjAco9bQ8NqNQlwo7cTffA5ZnMCbY2qODFre77yQBV44May3tsL5CQxYDqmvqXL0cJUSqmrM9YTHSCsfchsATzRbjCpxrcV9vPYqhQh71l+piQI1fnn25l3TwdThqG07dOtRH/rc8jnOHsC85PdAtzL2E6UGJF9kjTcWr/Bc1F1fS4+asz2VDGS+B6TsGbuVVNLYQfrk21ZmM4UoPpPsODJq0755jsrBBhpy981XOcbaWq3K6VBPq07q5m69KbaKyLjBGyOWHyvx+C9R/s4Q==~3491141~4277830'
    }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url, headers, method='POST', data=payload)
        if response is None:
            return []  # Return an empty list if the response is None due to a content type error

        articles = response.get("posts", [])

        detailed_articles = []
        for article in articles:
            headline = article.get("title", "No title")
            summary = article.get("description", "No summary")
            article_url = article.get("url", "No URL")
            publish_date = article.get("displayDate", "No date")

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
                    'source': 'McKinsey',
                    'keywords': ', '.join(matched_keywords)
                }
                save_article(article_record)
                detailed_articles.append(article_record)

        return detailed_articles

async def scrape_articles_from_html():
    url = "https://www.mckinsey.com/featured-insights/future-of-asia/overview"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'OptanonAlertBoxClosed=2024-04-11T06:16:49.934Z; at_check=true; AMCVS_95851C8B53295A6D0A490D4D%40AdobeOrg=1; McKinseySessionID=104.109.251.46.13306631716990380939; shell^#lang=en; AKA_A2=A; _abck=38FD117C8AB086C741A9806C383E5ABC~0~YAAQBvttaEnu0cOQAQAA8wMA/QxCTN9R1TJfFgsRh7w31/ov2DVLzPLY/iiuAzen4e5ae/Hf11xP5O9N3eXkHdVoS+cLvhSSrrIEhl8T4R4pG/PunGqXBiTa5G1OPYNz7dyGXcOpKw6gGYqkLzFUfphlyF2OG5tOsmXLx4AzCtH1DqBAFtPG76bInmDnRrOx3Cu+6EOrC9xrq2zFocwJyqZ95EASjhQrPTSNmoqme+jue7WqCs7it+pqfVCFvbAWUat0TjZqikIjryrQNTXGM45XHGz7CwqW7fmb3yHwhiQ3xTyrsg2M9HSDmHCQezKztT2Cz/yy2em9qaSGg4MBlIk5cDsIVKXiJBgO8t3Zo3Ok87l7dGcv6uT/FqEKss5ghzWSe4gK7MHt7wLYXL9+hjejwT0gq/qphJw=~-1~-1~-1; ak_bmsc=9AFFABB440C1E15AE154BB5F80C70D81~000000000000000000000000000000~YAAQBvttaEru0cOQAQAA8wMA/RjalFL4XAfCyOUpWvQITgv+xB0Q8WEADJUrcWRHoEa+cbjeGSc43kUbhb/Lnjc/zA1vSQNSBcbH/qWDYqwJOCyQn6kqfGVmcTCe0CaibbP+ZUS/0m1SN/XO9ZJ3I2K4EE1kILedLSYJFFoF0WLhQvCc/kKTwetyjUrApnSs2yg3GuhiRLu3BAkPQR5SlQaefE9VDgD1udwwEiNrEuQLNyhYXg2qoaSJHVQEToNyBQsMuLjmrHcm3Qa+wV71iAgHpi95rJkrHgipeSrsyJU5pj7Opn+aBTgYcTgLdOyJE9rLUTu9g+GlC7Uv/Xez+QXqDgSOkcH8tboFAEsL/9iTqeBIAg8HUyiBLcKeNeoTsZC+2E9eS4FLtyA=; bm_mi=040A317EC529A020C87285484A17C2E4~YAAQBvttaGn40cOQAQAAFb0B/Rir034WfWiMV5Lg32uNOqDT4emdm6R1XEa7VJFjxJKzEuQ1UeNNS8mW9BfUXA0Ze3c8C55gmn9d1j6/jJ9VqYt1Ci/vCCzmQU3G2s7U+f2+sjaJJeKnGnzCr7N27gCPq2/YS6GAHPx1mUzzMA35pqkxXuKkzkgVorvPMpKo72aYiqAi/BrdtS1jRD1vl29ZMx/CdefhtrdfEnseXrAfJmp1I5m3Hr+PT0TQ5Z4Q3bDfmFSLNx0Uzqnm+hXh7gaUlfUXm113o3rcwer9CKFHK+zNOzwDqjJwXvujz5MSB5PPyGicRTKmWkdMxlTHn1pRDJ8UgdXP+ob808B0NNjXgVF6faDoo6Lii4+DzqajCM4g0L1Btao327vFBPwYNPrCaDJVGngf5Q==~1; bm_sv=A83DA1A04BEFF06AFD38E577816C7DBC~YAAQBvttaGr40cOQAQAAFr0B/Rg0hh0Mro24NYRhLa9stKsK4EEkaO4rY0wXRCYzhtbL7fq35K3nWZqsieABLCEbjqz0LGSMibF/Jo0Nl9ILPmf6T3+dFWaiY4AjojxrkecZpQ3Nm/ZjNd/d5hmha7Ae8CxW6cFICea+L1ntvcnePQNNcmV5S9gqY7HSSxjRR9EWPBJ7FRO92N7qpcJpBJC2THBigdsxVSNczc9lV+ribxSUVl+HpKkiGhbU9YTW0QE=~1; bm_sz=B0C87E7413226CDE44D7F132075819A5~YAAQBvttaGv40cOQAQAAFr0B/RhW7n81t2lK0Rksx3ETWzc6y8r/4RPoWE9gLv2uqDA9XTuzi4wDX7RERFm435IIpih+W8cW+7nrcJ4DM0gJDxZ50ZAxYkVGm1Wii99fMgbNgKqgkyHRSqmT1qKZh0jd7Weq6xWcYjFPierajHEFS4aE65CWSMUsH+CQQ48JadJebDeYxak7DcdazldfOSTXQaCwA67XbTkExXknrMjmeT/nqAtXJfxTIbuHZPta3HtHiH5RNpsNaK16bxaC3pd2xzQvg5XD7Gm+U4gxAY0dv/Uw4AFlf7C1Al0wT8LN9bxa9D94vmoMIu4lVhFRyuwDC4+vddMTodErU7eHJAaNPC+sFVMIsN2srCWJOQj+/PKAmOUlq42feNIpG/yV5Itxe041W68NXGNaaAs=~3421761~3420472',
        'priority': 'u=0, i',
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

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch URL: {url} with status code {response.status}")
                return []

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            articles = []

            for item in soup.find_all('div', class_='GenericItem_mck-c-generic-item__content__gq1m0'):
                title_tag = item.find('h5')
                link_tag = item.find('a')
                time_tag = item.find('time')
                summary_tag = item.find('div', class_='mck-u-links-inline mck-c-generic-item__description GenericItem_mck-c-generic-item__description--with-date__KRltZ')

                if title_tag and link_tag and 'href' in link_tag.attrs and time_tag and summary_tag:
                    title = title_tag.text.strip()
                    link = link_tag['href']
                    date = time_tag['datetime'] if 'datetime' in time_tag.attrs else time_tag.text
                    summary = summary_tag.text.strip()

                    matched_keywords = is_credit_rating_related(title, summary)
                    if not matched_keywords:
                        logging.debug(f"Skipping non-relevant article: {title}")
                        continue

                    article_record = {
                        'title': title,
                        'date': date,
                        'summary': summary,
                        'url': link,
                        'source': 'McKinsey',
                        'keywords': ', '.join(matched_keywords)
                    }
                    save_article(article_record)
                    articles.append(article_record)

            return articles

def run_mckinsey_articles():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mckinsey_articles())
    loop.run_until_complete(scrape_articles_from_html())

if __name__ == "__main__":
    run_mckinsey_articles()
