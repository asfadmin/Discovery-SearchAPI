import requests
import logging
import json
from asf_env import get_config

def get_cmr_health():
    r = requests.get('https://cmr.earthdata.nasa.gov/search/health')
    d = json.loads(r.text)
    return d
