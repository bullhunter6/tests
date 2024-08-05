import requests
from bs4 import BeautifulSoup
from dateutil import parser
from utils.event_db_utils import save_events
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_date(date_str, part='start'):
    try:
        date_parts = date_str.split()
        if len(date_parts) == 3:  # Single date format
            day = date_parts[0]
            month = date_parts[1]
            year = date_parts[2]
            date_str = f"{day} {month} {year}"
            date = parser.parse(date_str, dayfirst=True)
        elif len(date_parts) == 5:  # Date range format
            start_day = date_parts[0]
            end_day = date_parts[2]
            month = date_parts[3]
            year = date_parts[4]
            if part == 'start':
                date_str = f"{start_day} {month} {year}"
            else:
                date_str = f"{end_day} {month} {year}"
            date = parser.parse(date_str, dayfirst=True)
        else:
            raise ValueError("Unexpected date format")
        return date.strftime('%Y/%m/%d')
    except Exception as e:
        logging.error(f"Error parsing date: {e}")
        return "Invalid date"

def get_adb_events():
    logging.info("Fetching ADB events...")
    url = "https://www.adb.org/news/events/calendar"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_fbp=fb.1.1715781146905.2132411980; _gcl_au=1.1.551677385.1715781147; cookie-agreed-version=1.0.0; cookie-agreed=2; _gid=GA1.2.1029616534.1722577397; _clck=svbiai%7C2%7Cfnz%7C0%7C1596; _ga=GA1.2.1904632270.1715781147; _clsk=k6g6od%7C1722577410081%7C2%7C1%7Cu.clarity.ms%2Fcollect; _ga_XZTWST314D=GS1.1.1722577396.8.1.1722577456.0.0.0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    events = []
    event_lists = soup.find_all('div', class_='item-list item-list-divider item-list-events')
    for event_list in event_lists:
        month = event_list.find('h3').text.strip()
        for event in event_list.find_all('li'):
            date = event.find('span', class_='event-date').text.strip()
            title_tag = event.find('span', class_='event-title')
            title = title_tag.text.strip()
            location = event.find('span', class_='event-location').text.strip()
            details_tag = event.find('span', class_='event-details')
            details = details_tag.text.strip() if details_tag else "No additional details available."
            link = "https://www.adb.org" + title_tag.find('a')['href']
            start_date = format_date(date, part='start')
            end_date = format_date(date, part='end')
            events.append({
                "title": title,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "details": details,
                "link": link,
                "source": "ADB"
            })
    save_events(events)  # Save events to database
    logging.info("ADB events fetched and saved successfully.")
    return events
