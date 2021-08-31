import logging
import multiprocessing
import time

import requests
from flask import request
from urllib.parse import urlparse
from asf_env import get_config


def analytics_events(events=None):
    if events is None or len(events) == 0:
        return

    cfg = get_config()
    analytics_id = cfg['analytics_id']

    if analytics_id is None:
        logging.debug('Skipping analytics: analytics_id not set')
        return

    logging.debug(f'Posting {len(events)} analytics events to {analytics_id}')

    params = {
        "v":    "1",
        "tid":  analytics_id,
        "cid":  f'{request.access_route[-1]}'
    }

    events_with_params = [
        combine_event_and_params(params, event) for event in events
    ]

    start = time.time()
    try:
        if len(events) == 1:
            post_analytics_event(events_with_params[0])
        else:
            num_processes = min([8, len(events)])
            p = multiprocessing.pool.ThreadPool(processes=num_processes)

            p.map_async(post_analytics_event, events_with_params)
            p.close()
            p.join()

    except requests.RequestException as e:
        logging.debug(f'Problem logging analytics: {e}')

    end = time.time()
    logging.debug(f'ANALYTICS TOOK {end - start}')


def combine_event_and_params(params, event):
    p = dict(params)
    p['t'] = 'event'
    p['ec'] = event['ec']
    p['ea'] = event['ea']

    return p


def post_analytics_event(event):
    logging.debug(f'POSTING EVENT {event}')

    session = requests.Session()
    url = get_analytics_url()
    session.post(url, data=event)


def get_analytics_url():
    return "http://www.google-analytics.com/collect"


def analytics_pageview():
    if get_config()['analytics_id'] is None:
        logging.debug('Skipping analytics: analytics_id not set')
        return

    logging.debug(f'Posting analytics pageview to {get_config()["analytics_id"]}'
    url = get_analytics_url()
    params = {
        "v":    "1",
        "tid":  get_config()['analytics_id'],
        "cid":  f'{request.access_route[-1]}'
        }
    try:
        s = requests.Session()
        p = dict(params)
        p['t'] = 'pageview'
        p['uip'] = request.access_route[-1]
        p['dr'] = request.referrer
        api_url = get_config().get('this_api')
        if api_url is not None:
            api_url = urlparse(api_url)
            api_url = api_url.geturl().replace(api_url.scheme + "://", "") # take out the scheme
            p['dh'] = api_url                                              # Needed for proper hostname on AWS API Gateway
            p['dp'] = request.full_path
        else:
            p['dl'] = request.url # default to just blindly using the request url
        p['ua'] = request.headers.get('User-Agent')
        s.post(url, data=p)
    except requests.RequestException as e:
        logging.debug(f'Problem logging analytics: {e}')
