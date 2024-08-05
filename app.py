from datetime import datetime, timedelta
from flask import Flask, render_template, request
from utils.db_utils import create_db, get_articles_by_date, get_articles_by_source, get_articles_by_date_and_source, get_latest_articles
from utils.event_db_utils import create_events_db, get_events
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_date_range():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    return today.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')

@app.route('/')
def home():
    date = request.args.get('date')
    source = request.args.get('source')
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    
    if date and source:
        logging.debug(f"Filtering articles by date: {date} and source: {source}")
        articles = get_articles_by_date_and_source(date, source)
        headline = f"Articles from {date} and Source: {source}"
    elif date:
        logging.debug(f"Filtering articles by date: {date}")
        articles = get_articles_by_date(date)
        headline = f"Articles from {date}"
    elif source:
        logging.debug(f"Filtering articles by source: {source}")
        articles = get_articles_by_source(source)
        headline = f"Articles from Source: {source}"
    else:
        logging.debug("Fetching latest articles")
        articles = get_latest_articles(today, yesterday)
        headline = "Latest Articles"
        
    logging.debug(f"Number of articles fetched: {len(articles)}")
    return render_template('home.html', articles=articles, title="Home", headline=headline, current_date=date, current_source=source)

@app.route('/events')
def events():
    date = request.args.get('date')
    source = request.args.get('source')
    
    logging.info("Fetching events from the database...")
    
    if date and source:
        logging.debug(f"Filtering events by date: {date} and source: {source}")
        events = get_events(date=date, source=source)
        headline = f"Events from {date} and Source: {source}"
    elif date:
        logging.debug(f"Filtering events by date: {date}")
        events = get_events(date=date)
        headline = f"Events from {date}"
    elif source:
        logging.debug(f"Filtering events by source: {source}")
        events = get_events(source=source)
        headline = f"Events from Source: {source}"
    else:
        logging.debug("Fetching upcoming events")
        events = get_events(upcoming=True)
        headline = "Upcoming Events"
        
    logging.info(f"Number of events fetched: {len(events)}")
    return render_template('events.html', events=events, title="Events", headline=headline, current_date=date, current_source=source)

if __name__ == '__main__':
    create_db()
    create_events_db()
    app.run(debug=True)
