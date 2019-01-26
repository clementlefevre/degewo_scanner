
# coding: utf-8

import requests
import time
import pandas as pd
from sqlalchemy import create_engine
import logging
from random import randint
from config import DEGEWO_GET_TIMER,EXCEL_FILE

logger = logging.getLogger(__name__)



ROOT_URL = "https://immosuche.degewo.de"
START_URL = ROOT_URL + "/de/search.json?utf8=✓&property_type_id=1&district=28%2C+71&page=1&rooms_radio=custom&rooms_from=3&rooms_to=10"

DESCRIPTION_ROOT_URL = "https://immosuche.degewo.de/de/properties/"


def get_json(url):
    r = requests.get(url)
    #logging.debug('_'.join([str(r.status_code),r.headers['content-type'],r.encoding]))
    result = r.json()
    return result


def is_last_page(result):
    #print("current_page : "+result['pagination']['current_page'])
    #print("last_page    : "+result['pagination']['last_page'])
    #print(result['pagination']['current_page']==result['pagination']['last_page'])
    last_page_reached =  result['pagination']['current_page']==result['pagination']['last_page']
    no_pages_at_all = 'page=0' in result['pagination']['last_page']
    
    return last_page_reached | no_pages_at_all


def retrieve_offers():
    result = get_json(START_URL)
    if len(result['immos'])<1:
        logging.info('No offers found')
        return pd.DataFrame()
    
    df_offers = pd.DataFrame(result['immos'])
    while not is_last_page(result):
        time.sleep(DEGEWO_GET_TIMER+randint(-5,5))
        result = get_json(ROOT_URL+result['pagination']['next_page'])
        df_offers = pd.concat([df_offers,pd.DataFrame(result['immos'])])
        
    return df_offers


def reformat_df(df_retrieved):
    df_retrieved = pd.concat([df_retrieved.drop(['authority','external_data'],axis=1),df_retrieved.authority.apply(pd.Series)],axis=1)
    df_retrieved = pd.concat([df_retrieved.drop(['location'],axis=1),df_retrieved.location.apply(pd.Series)],axis=1)
    df_retrieved['url']= DESCRIPTION_ROOT_URL + df_retrieved['id'].astype(str)
    df_retrieved = df_retrieved.set_index('url').reset_index()

    return df_retrieved



def write_new_offers_to_db(df_retrieved):

    disk_engine = create_engine('sqlite:///degewo.db')

    try:
        df_current_db = pd.read_sql_query('SELECT * FROM immos',disk_engine)
        
    except:
        df_current_db = pd.DataFrame()
        df_current_db['url']=0


    # filter on id not yet in db
    #import ipdb; ipdb.set_trace()
    df_new_offers = df_retrieved[~df_retrieved['url'].isin(df_current_db['url'].tolist())]
    if df_new_offers.shape[0]<1:
        logging.info('No new offers found')

    df_new_offers.astype(str).to_sql('immos', disk_engine, if_exists='append')
    disk_engine.dispose()

    logging.info("new offers saved into DB :{} offers".format(df_new_offers.shape[0]))
    df_retrieved.to_excel(EXCEL_FILE)
    return(df_new_offers)



