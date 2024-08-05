import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_events_db():
    logging.info("Initializing the database...")
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY,
                  title TEXT,
                  start_date TEXT,
                  end_date TEXT,
                  location TEXT,
                  details TEXT,
                  link TEXT,
                  source TEXT,
                  UNIQUE(title, start_date))''')
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully.")

def save_events(events):
    logging.info(f"Saving {len(events)} events to the database...")
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    for event in events:
        try:
            c.execute('''INSERT INTO events (title, start_date, end_date, location, details, link, source)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                      (event['title'], event['start_date'], event['end_date'], event['location'], event['details'], event['link'], event['source']))
        except sqlite3.IntegrityError:
            logging.info(f"Duplicate event found: {event['title']} on {event['start_date']}. Skipping...")
    conn.commit()
    conn.close()
    logging.info("Events saved successfully.")


def get_events(upcoming=False, date=None, source=None):
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = 'SELECT title, start_date, end_date, location, details, link, source FROM events WHERE 1=1'
    params = []
    
    if upcoming:
        today = datetime.now().strftime('%Y/%m/%d')
        query += ' AND start_date >= ?'
        params.append(today)
    
    if date:
        try:
            date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%Y/%m/%d')
            query += ' AND start_date = ?'
            params.append(date_formatted)
        except ValueError:
            logging.error("Incorrect date format. It should be YYYY-MM-DD.")
    
    if source:
        query += ' AND source = ?'
        params.append(source)
    
    logging.debug(f"Executing query: {query} with params: {params}")
    c.execute(query, params)
    events = c.fetchall()
    conn.close()
    return events