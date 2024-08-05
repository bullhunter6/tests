import logging
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

from extractors.esma import esma_articles
from extractors.fca import fca_articles
from extractors.moodys import moodys_articles
from extractors.sec import sec_articles
from extractors.wef import wef_articles
from extractors.reuters import run_reuters_articles
from extractors.khaleej_times import run_khaleej_times_articles
from extractors.the_national_news import run_the_national_news_articles
from extractors.sca import run_sca_articles
from extractors.kpmg import kpmg_articles
from extractors.world_bank import world_bank_articles
from extractors.ifc import ifc_articles
from extractors.fitch import fitch_articles
from extractors.bcg import bcg_articles
from extractors.mck_1 import run_mckinsey_articles
from extractors.imf_1 import imf_1_articles


from extractors.events.adb import get_adb_events
from extractors.events.ifc import get_ifc_events

from utils.event_db_utils import create_events_db

logging.basicConfig(level=logging.DEBUG)

def run_extractors():
    logging.info("Running extractors...")
    esma_articles()
    fca_articles()
    moodys_articles()
    sec_articles()
    wef_articles()
    #asyncio.run(run_reuters_articles())
    run_khaleej_times_articles()
    run_the_national_news_articles()
    run_sca_articles()
    kpmg_articles()
    world_bank_articles()
    #imf_1_articles()
    ifc_articles()
    run_mckinsey_articles()
    fitch_articles()
    bcg_articles()
    get_adb_events()
    get_ifc_events()
    logging.info("Extractors run completed.")

def start_scheduler():
    scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': 3600})
    scheduler.add_job(run_extractors, 'interval', minutes=30)
    scheduler.start()
    logging.info("Scheduler started.")
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Scheduler shut down.")

if __name__ == '__main__':
    create_events_db()
    run_extractors()
    #start_scheduler()
