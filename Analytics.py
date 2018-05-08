import requests
import logging

def post_analytics(r, category, action):
    url = "http://www.google-analytics.com/collect"
    params = {
        "v":    "1",
        "tid":  "UA-118881300-1",
        "cid":  "555",
        "t":    "event",
        "uip":  r.access_route[-1],
        "dr":   r.referrer,
        "dl":   r.url,
        "ec":   category,
        "ea":   action}
    try:
        requests.post(url, data = params)
    except requests.RequestException as e:
        logging.debug('Problem logging analytics: {0}'.format(e))