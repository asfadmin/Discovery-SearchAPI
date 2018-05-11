import requests
import logging
from flask import request
from md5 import md5

def post_analytics(events=None, pageview=False):
    url = "http://www.google-analytics.com/collect"
    params = {
        "v":    "1",
        "tid":  "UA-118881300-2",
        "cid":  md5(request.access_route[-1]).hexdigest()
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