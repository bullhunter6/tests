import sqlite3
from contextlib import closing
import logging

logging.basicConfig(level=logging.DEBUG)

def create_db():
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS articles (
                                id INTEGER PRIMARY KEY,
                                title TEXT,
                                date TEXT,
                                summary TEXT,
                                url TEXT UNIQUE,
                                source TEXT,
                                keywords TEXT
                              )''')
            conn.commit()
            logging.debug("Database created or already exists.")

def article_exists(url):
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''SELECT COUNT(*) FROM articles WHERE url = ?''', (url,))
            return cursor.fetchone()[0] > 0

def save_article(article):
    if article_exists(article['url']):
        logging.debug(f"Duplicate article found, not saving: {article['title']}")
        return
    
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''INSERT INTO articles (title, date, summary, url, source, keywords) 
                              VALUES (?, ?, ?, ?, ?, ?)''', 
                           (article['title'], article['date'], article['summary'], article['url'], article['source'], article['keywords']))
            logging.debug(f"Article saved to database: {article['title']}")
            conn.commit()

def get_articles_by_date(date):
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''SELECT title, date, summary, url, source, keywords FROM articles WHERE date = ? ORDER BY date DESC''', (date,))
            articles = cursor.fetchall()
            logging.debug(f"Articles fetched by date ({date}): {len(articles)}")
            return articles

def get_articles_by_source(source):
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''SELECT title, date, summary, url, source, keywords FROM articles WHERE source = ? ORDER BY date DESC''', (source,))
            articles = cursor.fetchall()
            logging.debug(f"Articles fetched by source ({source}): {len(articles)}")
            return articles

def get_articles_by_date_and_source(date, source):
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''SELECT title, date, summary, url, source, keywords FROM articles WHERE date = ? AND source = ? ORDER BY date DESC''', (date, source))
            articles = cursor.fetchall()
            logging.debug(f"Articles fetched by date ({date}) and source ({source}): {len(articles)}")
            return articles

def get_latest_articles(today, yesterday):
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''SELECT title, date, summary, url, source, keywords FROM articles 
                              WHERE date IN (?, ?)
                              ORDER BY date DESC''', (today, yesterday))
            articles = cursor.fetchall()
            logging.debug(f"Latest articles fetched: {len(articles)}")
            return articles


def get_articles():
    """Retrieve all articles from the database."""
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''SELECT title, date, summary, url, source FROM articles ORDER BY date DESC''')
            articles = cursor.fetchall()
            return articles
