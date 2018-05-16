import requests
import logging
from flask import request
from asf_env import get_config

def post_analytics(events=None, pageview=False):
    if get_config()['analytics_id'] is None:
        logging.debug('Skipping analytics: analytics_id not set')
        return
    logging.debug('Posting analytics to {0}'.format(get_config()['analytics_id']))
    url = "http://www.google-analytics.com/collect"
    params = {
        "v":    "1",
        "tid":  get_config()['analytics_id'],
        "cid":  '{0}'.format(request.access_route[-1])
        }
    try:
        s = requests.Session()
        if pageview:
            p = dict(params)
            p['t'] = 'pageview'
            p['uip'] = request.access_route[-1]
            p['dr'] = request.referrer
            p['dl'] = request.url
            s.post(url, data=p)
        for e in events:
            p = dict(params)
            p['t'] = 'event'
            p['ec'] = e['ec']
            p['ea'] = e['ea']
            s.post(url, data=p)
    except requests.RequestException as e:
        logging.debug('Problem logging analytics: {0}'.format(e))