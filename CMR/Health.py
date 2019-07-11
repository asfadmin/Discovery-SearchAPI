import requests
import logging
import json
from asf_env import get_config

def get_cmr_health():
    cfg = get_config()
    try:
        r = requests.get(cfg['cmr_base'] + cfg['cmr_health'], timeout=10)
        d = {'host': cfg['cmr_base'], 'health': json.loads(r.text)}
    except Exception as e:
        logging.debug(e)
        d = {'host': cfg['cmr_base'], 'error': '{0}'.format(e)}
    return d
