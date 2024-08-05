import sqlite3
from contextlib import closing
import logging

logging.basicConfig(level=logging.DEBUG)

DATABASE = 'articles.db'

def get_duplicate_articles():
    with closing(sqlite3.connect(DATABASE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT url, COUNT(*) as cnt 
                FROM articles 
                GROUP BY url 
                HAVING cnt > 1
            ''')
            duplicates = cursor.fetchall()
            logging.debug(f"Found {len(duplicates)} duplicate articles.")
            return duplicates

def delete_duplicate_articles():
    duplicates = get_duplicate_articles()
    
    with closing(sqlite3.connect(DATABASE)) as conn:
        with closing(conn.cursor()) as cursor:
            for url, count in duplicates:
                cursor.execute('''
                    SELECT id 
                    FROM articles 
                    WHERE url = ?
                ''', (url,))
                ids = cursor.fetchall()

                # Keep the first article, delete the rest
                for article_id in ids[1:]:
                    cursor.execute('''
                        DELETE FROM articles 
                        WHERE id = ?
                    ''', (article_id[0],))
                    logging.debug(f"Deleted duplicate article with id {article_id[0]}")

            conn.commit()

if __name__ == '__main__':
    delete_duplicate_articles()
    logging.info("Duplicate articles deleted.")
