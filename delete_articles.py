import sqlite3
from contextlib import closing
import logging

logging.basicConfig(level=logging.DEBUG)

def delete_world_bank_articles():
    """Delete all articles from the 'World Bank' source in the database."""
    with closing(sqlite3.connect('articles.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("DELETE FROM articles WHERE source = 'IMF'")
            conn.commit()
            logging.debug("All 'World Bank' articles have been deleted from the database.")

if __name__ == '__main__':
    delete_world_bank_articles()
    logging.info("Deletion complete.")
