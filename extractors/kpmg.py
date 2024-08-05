import requests
import json
from datetime import datetime
from utils.db_utils import save_article
import logging
from utils.keywords import CREDIT_RATING_KEYWORDS

logging.basicConfig(level=logging.DEBUG)


def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    return any(keyword.lower() in content for keyword in CREDIT_RATING_KEYWORDS)

def kpmg_articles():
    url = "https://kpmg.com/esearch/xx-en"

    payload = json.dumps({
        "query": "",
        "filters": {
            "all": [
                {
                    "kpmg_tab_type": [
                        "Insights"
                    ]
                },
                {
                    "kpmg_article_type": [
                        "Article-General"
                    ]
                },
                {
                    "kpmg_template_type": [
                        "article-details-template",
                        "insights-flexible-template",
                        "editable-flex-template",
                        "editable-campaign-template"
                    ]
                }
            ]
        },
        "result_fields": {
            "kpmg_description": {
                "raw": {}
            },
            "kpmg_banner_flag": {
                "raw": {}
            },
            "kpmg_primary_tag": {
                "raw": {}
            },
            "kpmg_article_date": {
                "raw": {}
            },
            "kpmg_contact_job_ttl": {
                "raw": {}
            },
            "kpmg_title": {
                "raw": {}
            },
            "kpmg_contact_city": {
                "raw": {}
            },
            "kpmg_event_start_time": {
                "raw": {}
            },
            "kpmg_article_date_time": {
                "raw": {}
            },
            "kpmg_tab_type": {
                "raw": {}
            },
            "kpmg_short_desc": {
                "raw": {}
            },
            "kpmg_image_alt": {
                "raw": {}
            },
            "kpmg_url": {
                "raw": {}
            },
            "kpmg_template_type": {
                "raw": {}
            },
            "kpmg_image": {
                "raw": {}
            },
            "kpmg_non_decorative_alt_text": {
                "raw": {}
            },
            "kpmg_article_readtime": {
                "raw": {}
            },
            "kpmg_contact_fn": {
                "raw": {}
            },
            "kpmg_contact_ln": {
                "raw": {}
            },
            "kpmg_event_type": {
                "raw": {}
            },
            "kpmg_contact_country": {
                "raw": {}
            },
            "kpmg_is_rendition_optimized": {
                "raw": {}
            },
            "kpmg_article_primary_format": {
                "raw": {}
            },
            "kpmg_article_type": {
                "raw": {}
            },
            "kpmg_event_startdate": {
                "raw": {}
            }
        },
        "page": {
            "size": 20,
            "current": 1
        },
        "sort": {
            "kpmg_filter_date": "desc"
        }
    })
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'cookie': 'gig_canary=false; visit_settings=%7B%22count%22%3A3%2C%22mins%22%3A30%2C%22days%22%3A14%7D; sat_track=true; gig_bootstrap_3_e2ggAN5_ZqWrSNeM0HSHMYT8P16JqxINgs88bIrpCmPIiLJZ4zOqT69Wy7I6UByO=login_ver4; gig_bootstrap_3_eYey6Z79si-eeXEPJdZ-nHmhuCW-jna6Vvc90U_rCKgSJBvRulOycPAZkI--y8OB=login_ver4; gig_canary_ver=16174-3-28698555; visit_count=1721913581897-1-1723123178465',
        'origin': 'https://kpmg.com',
        'priority': 'u=1, i',
        'referer': 'https://kpmg.com/xx/en/home/insights.html',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()

    articles = data.get("results", [])
    for article in articles:
        title = article.get("kpmg_title", {}).get("raw", "No title")
        description = article.get("kpmg_description", {}).get("raw", "No description")
        date = article.get("kpmg_article_date", {}).get("raw", "No date")
        url = article.get("kpmg_url", {}).get("raw", "No URL")

        if not is_credit_rating_related(title, description):
            logging.debug(f"Skipping non-relevant article: {title}")
            continue

        # Format the date
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z").strftime('%Y-%m-%d')
        except ValueError:
            parsed_date = date

        article_data = {
            'title': title,
            'date': parsed_date,
            'summary': description,
            'url': url,
            'source': 'KPMG'
        }
        save_article(article_data)
        logging.debug(f"Saved article to database: {title}")
