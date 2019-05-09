import requests
import logging
import json
from asf_env import get_config

def get_cmr_health():
    cfg = get_config()
    r = requests.get(cfg['cmr_base'] + cfg['cmr_health'])
    d = {'host': cfg['cmr_base'], 'health': json.loads(r.text)}
    return d
