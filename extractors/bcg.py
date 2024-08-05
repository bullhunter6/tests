import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from utils.db_utils import save_article
import logging
import re
from utils.keywords import CREDIT_RATING_KEYWORDS

logging.basicConfig(level=logging.DEBUG)

def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    matched_keywords = [keyword for keyword in CREDIT_RATING_KEYWORDS if keyword.lower() in content]
    return matched_keywords

def bcg_articles():
    url = "https://www.bcg.com/search?q=credit+rating&s=0&f6=00000171-eb9f-d340-ad71-eb9fe4600000&f7=00000171-f17b-d394-ab73-f3fbae0d0000&f3=00000172-0efd-d58d-a97a-5eff51730014&f6=00000171-eb9f-d340-ad71-eb9fe4600000"

    payload = {}
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'BCG-GEO=Country=AE&Continent=AS; akaalb_ALB_www=~op=ALB_beta:Beta_Europe|~rv=13~m=Beta_Europe:0|~os=99426c3199c2b5e7edf93918d715c120~id=46bcf5df4cbcb67549f4a708e445243a; ak_cdataval=4b77d0f4a33f519e4b5e49b63564079b; AMCVS_0B2D2B6956FA77C27F000101%40AdobeOrg=1; ak_bmsc=09932EEF0AC2D02B1743CB5E2BA451B8~000000000000000000000000000000~YAAQLPttaHnGdP6QAQAAHHoRAhimUZ6+P0NqUXDqAjNQFaJBcurBeLjeOkMcWW11glz8z1Ozcme27CL2u/lOFJmvHapxgEJziFEBvxMsx+cY5qKCRLy21ZFK8pBQNGN9xb8CC14lrApSiciyedV6UnZQFxcQM71M+T+CrNXEgqNL5D2DJoyzap3lt8OFXUmltDzrJDXfcsVub7WV1xlGkgbSdJkAedvPKSjT3VlHWAO3PjmeNVLoltJgyzwZba5rG3utsWpqSBRIACvWSwLcz0bVNA19GApHMa2ztYtHMEJD0czMOdaqppPMDXucyHzghAwXL24Pn5NvHCD51LrHMzkIBkInvihb/vUtzJbswtEVyuqZcL44eVCP+ZwxqBr4kNtSNAQl; TAsessionID=208391de-ea50-4bcc-a8e4-37bf43791079|NEW; notice_behavior=implied,eu; AMCV_0B2D2B6956FA77C27F000101%40AdobeOrg=1176715910%7CMCIDTS%7C19935%7CMCMID%7C02940136414690501021301224143168717096%7CMCAID%7CNONE%7CMCOPTOUT-1722323804s%7CNONE%7CvVersion%7C5.4.0; bm_sv=EEC41EF66799691DCA0D7759FDA5E078~YAAQLPttaLjIdP6QAQAAvzgSAhi27+iBDOw5wYWjHL/vnI3LdKVe0mXhVi9LA9/aikIX0nZ+i7ZDYHg7pkUGD82EI4EOzObvEi0bC6/ID5OB17w4WsaG2+Bekmb+VTcEseh7k7SwLIZXLH18faWwsFFarEuAgFrSSkGUFmnKR1ZR/psk2s97yr1QQBpb1TTomlc6LxeZYUeX4pBKepV/nvsDp0SoVrzWNcLnTkxO2g495shOoveNT2x3ABDz~1; bm_sv=EEC41EF66799691DCA0D7759FDA5E078~YAAQLPttaD/LdP6QAQAAexsTAhgjeXeKlSP5YGAv0LmYxfIPlO9A3oxh3FkXgwP90K+RB/pyP0GPNiX0fq2rPd6Ogj1dpTkjepP20zOOmR1mJAFtVTOrt2HMpN38vFZ5WTHV09VxAeIGY3A6UHNoVc/K8w3Eqfo/g3/X7MjbILxmvh7J++hEnIxOLEpbxU5/pyt/WaX0/aiCMbklwuSteYh6gFo/E7qXZro1D3vAHpft14SD+Gf53cVDVaC7~1; BCG-GEO=Country=AE&Continent=AS; ak_cdataval=bddc373cad1043808437b9b5b20920f3',
        'priority': 'u=1, i',
        'referer': 'https://www.bcg.com/search?q=credit+rating&s=0&f6=00000171-eb9f-d340-ad71-eb9fe4600000&f7=00000171-f17b-d394-ab73-f3fbae0d0000&f3=00000172-0efd-d58d-a97a-5eff51730014&f6=00000171-eb9f-d340-ad71-eb9fe4600000',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    articles = []

    for article in soup.find_all('section', class_='search-result', attrs={'data-display-type': 'Standard Article'}):
        title = article.find('h2', class_='title').text.strip()
        link = article.find('a', class_='Link')['href']
        subtitle = article.find('p', class_='subtitle').text.strip()
        date = re.search(r'\| (.+)', subtitle)
        published_date = date.group(1) if date else 'Unknown'
        summary = article.find('p', class_='intro').text.strip()
        
        matched_keywords = is_credit_rating_related(title, summary)
        if not matched_keywords:
            logging.debug(f"Skipping non-relevant article: {title}")
            continue

        try:
            parsed_date = date_parser.parse(published_date).strftime('%Y-%m-%d')
            logging.debug(f"Parsed date: {parsed_date} for article: {title}")
        except (ValueError, TypeError) as e:
            logging.error(f"Invalid date format for article: {title} with date: {published_date}")
            continue

        article_data = {
            'title': title,
            'url': link,
            'date': parsed_date,
            'summary': summary,
            'source': 'BCG',
            'keywords': ', '.join(matched_keywords)
        }

        save_article(article_data)
        logging.debug(f"Saved article to database: {title}")
        articles.append(article_data)

    return articles
