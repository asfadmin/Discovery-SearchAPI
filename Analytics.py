import requests
import logging
from flask import request

def post_analytics(ec, ea):
    url = "http://www.google-analytics.com/collect"
    params = {
        "v":    "1",
        "tid":  "UA-118881300-1",
        "cid":  "555",
        "t":    "event",
        "uip":  request.access_route[-1],
        "dr":   request.referrer,
        "dl":   request.url,
        "ec":   ec,
        "ea":   ea}
    try:
        requests.post(url, data = params)
    except requests.RequestException as e:
        logging.debug('Problem logging analytics: {0}'.format(e))