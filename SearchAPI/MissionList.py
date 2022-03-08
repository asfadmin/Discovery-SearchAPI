from SearchAPI.asf_env import get_config
from defusedxml.lxml import fromstring

import logging
import requests


def getMissions(data):
    cfg = get_config()

    r = requests.post(cfg['cmr_base'] + cfg['cmr_collections'], headers=cfg['cmr_headers'], data=data)
    if r.status_code != 200:
        return { 'errors': [{'type': 'CMR_ERROR', 'report': f'CMR Error: {r.text}'}]}

    try:
        root = fromstring(r.text.encode('latin-1'))
    except Exception as e:
        return {'errors': [{'type': 'CMR_ERROR', 'report': f'Error parsing XML from CMR: {e}'}]}

    missions = [f.text for f in root.findall('.//facets/facet[@field="project"]/value')]
    missions = sorted(missions, key=lambda s: s.casefold())
    logging.debug(missions)

    # All done
    return { 'result': missions }
