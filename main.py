import logging
import time
import schedule
from service.send_email import send_notification
from service.degewo_scrapper import scrapper
from query_config import query_christin, query_elise


logging.basicConfig(
    filename="degewo.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def job():
    logging.info("Job starts...")
    scrapper(query_christin)
    scrapper(query_elise)


schedule.every().day.at("05:15").do(job)

job()

while 1:
    schedule.run_pending()
    time.sleep(1)
