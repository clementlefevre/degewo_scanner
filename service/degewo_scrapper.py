# coding: utf-8

from collections import namedtuple
import requests
import time
import pandas as pd
import logging
from random import randint
from config import DEGEWO_GET_TIMER
from service.send_email import send_notification
import pathlib

logger = logging.getLogger(__name__)


ROOT_URL = "https://immosuche.degewo.de"
START_URL = ROOT_URL + "/de/search.json"
DESCRIPTION_ROOT_URL = "https://immosuche.degewo.de/de/properties/"


def get_json(url=None, query_string=None):

    r = requests.get(url, params=query_string)
    result = r.json()
    # logger.info("for {0} : {1} found".format(r.url, len(result["immos"])))
    return result


def is_last_page(result):
    last_page_reached = (
        result["pagination"]["current_page"] == result["pagination"]["last_page"]
    )
    no_pages_at_all = "page=0" in result["pagination"]["last_page"]

    return last_page_reached | no_pages_at_all


def retrieve_offers(query_string):

    result = get_json(START_URL, query_string)

    if len(result["immos"]) < 1:
        logging.info("No offers found")
        return pd.DataFrame()

    df_offers = pd.DataFrame(result["immos"])

    while not is_last_page(result):
        time.sleep(DEGEWO_GET_TIMER + randint(-5, 5))
        result = get_json(ROOT_URL + result["pagination"]["next_page"])
        df_offers = pd.concat([df_offers, pd.DataFrame(result["immos"])])

    return df_offers


def reformat_df(df_retrieved, query):
    df_retrieved = pd.concat(
        [
            df_retrieved.drop(["authority", "external_data"], axis=1),
            df_retrieved.authority.apply(pd.Series),
        ],
        axis=1,
    )
    df_retrieved = pd.concat(
        [
            df_retrieved.drop(["location"], axis=1),
            df_retrieved.location.apply(pd.Series),
        ],
        axis=1,
    )
    df_retrieved["url"] = DESCRIPTION_ROOT_URL + df_retrieved["id"].astype(str)
    df_retrieved["id_query"] = df_retrieved["id"].astype(str) + "_" + query.name
    df_retrieved = df_retrieved.drop_duplicates("id_query")
    df_retrieved = df_retrieved.set_index("url").reset_index()

    return df_retrieved


def save_sent_offers(df_retrieved):
    
    try:
        df_already_sent_offers = pd.read_csv("../sent_offers.csv")

    except Exception:
        print(f'file not found - current folder : {pathlib.Path(__file__).parent}')
        df_already_sent_offers = pd.DataFrame()
        df_already_sent_offers["id_query"] = 0

    # filter on id not yet in file
    df_new_offers = df_retrieved[
        ~df_retrieved["id_query"].isin(df_already_sent_offers["id_query"].tolist())
    ]
    if df_new_offers.shape[0] < 1:
        logging.info("No new offers found")

    df_new_offers.to_csv("../sent_offers.csv")
    logging.info("new offers saved  :{} offers".format(df_new_offers.shape[0]))

    return df_new_offers


def scrapper(query):
    logging.info(f'current folder : {pathlib.Path(__file__).parent}')
    df_online_offers = pd.DataFrame()

    try:
        for q in query.queries_string:
            offers_from_qs = retrieve_offers(q)

            df_online_offers = pd.concat([df_online_offers, offers_from_qs], axis=0)
            time.sleep(DEGEWO_GET_TIMER)

        if df_online_offers.shape[0] > 0:
            df_online_offers = reformat_df(df_online_offers, query)
            df_new_offers = save_sent_offers(df_online_offers)
            if df_new_offers.shape[0] > 0:
                send_notification(df_new_offers.url.tolist(), query)
    except Exception as e:
        logging.exception(e)
    finally:
        logging.info("Job done.")
