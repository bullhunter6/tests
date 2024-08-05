import requests
import json
from dateutil import parser
from utils.event_db_utils import save_events
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_date(date_str):
    try:
        date = parser.parse(date_str)
        return date.strftime('%Y/%m/%d')
    except Exception as e:
        logging.error(f"Error parsing date: {e}")
        return "Invalid date"

def get_ifc_events():
    logging.info("Fetching World Bank events...")
    url = "https://webapi.worldbank.org/aemsite/ifc/search"
    payload = json.dumps({
        "search": "*",
        "facets": [
            "contentType,sort:value,count:10000",
            "countries,sort:value,count:10000",
            "topics,sort:value,count:10000",
            "regions,sort:value,count:10000",
            "subTopics,sort:value,count:10000",
            "language,sort:value,count:10000"
        ],
        "filter": "(contentType eq 'Event') and (language eq 'English')",
        "count": True,
        "top": 20,
        "skip": 0,
        "orderby": "contentDate desc"
    })
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'ocp-apim-subscription-key': 'a02440fa123c4740a83ed288591eafe4',
        'origin': 'https://www.ifc.org',
        'priority': 'u=1, i',
        'referer': 'https://www.ifc.org/',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Cookie': '__cf_bm=pQbucevLJjJmYm_7DbHJpt3zcyl6v8fzXHJRdWyt8Y0-1722578733-1.0.1.1-vuTUmGBTlSx3RlCYh3mJFN4OvSQq7RGdh9wxrykW5MtwOCyCjIof56_9yikv6qhtwxFb4Cw9dW6YV9C.ARyilw; webapi.ApplicationGatewayAffinity=0cf43378eacc6df1d682f7a218da3255; webapi.ApplicationGatewayAffinityCORS=0cf43378eacc6df1d682f7a218da3255'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    events = []
    event_list = data.get('value', [])
    for event in event_list:
        title = event.get('title', 'No title')
        content_date = event.get('contentDate', 'No date')
        description = event.get('description', 'No description')
        location = "No location specified"
        link = "https://www.ifc.org" + event.get('pagePublishPath', '')
        start_date = format_date(content_date)
        events.append({
            "title": title,
            "start_date": start_date,
            "end_date": start_date,
            "location": location,
            "details": description,
            "link": link,
            "source": "World Bank"
        })
    save_events(events)
    logging.info("World Bank events fetched and saved successfully.")
    return events
