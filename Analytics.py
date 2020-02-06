import requests
import logging
from flask import request
from asf_env import get_config
import time


def analytics_events(events=None):
    if events is None:
        return

    cfg = get_config()
    analytics_id = cfg['analytics_id']

    if analytics_id is None:
        logging.debug('Skipping analytics: analytics_id not set')
        return

    logging.debug(f'Posting analytics events to {analytics_id}')
    url = "http://www.google-analytics.com/collect"

    params = {
        "v":    "1",
        "tid":  analytics_id,
        "cid":  f'{request.access_route[-1]}'
        }

    try:
        session = requests.Session()

        start = time.time()
        for event in events:
            p = dict(params)
            p['t'] = 'event'
            p['ec'] = event['ec']
            p['ea'] = event['ea']
            logging.debug(f'POSTING EVENT {p}')
            session.post(url, data=p)

        end = time.time()
        print(f'ANALYTICS TOOK {end - start}')

    except requests.RequestException as e:
        logging.debug('Problem logging analytics: {0}'.format(e))

def analytics_pageview():
    if get_config()['analytics_id'] is None:
        logging.debug('Skipping analytics: analytics_id not set')
        return
    logging.debug('Posting analytics pageview to {0}'.format(get_config()['analytics_id']))
    url = "http://www.google-analytics.com/collect"
    params = {
        "v":    "1",
        "tid":  get_config()['analytics_id'],
        "cid":  '{0}'.format(request.access_route[-1])
        }
    try:
        s = requests.Session()
        p = dict(params)
        p['t'] = 'pageview'
        p['uip'] = request.access_route[-1]
        p['dr'] = request.referrer
        p['dl'] = request.url
        p['ua'] = request.headers.get('User-Agent')
        s.post(url, data=p)
    except requests.RequestException as e:
        logging.debug('Problem logging analytics: {0}'.format(e))
