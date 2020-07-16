from asf_env import get_config

import logging
import requests
from lxml import etree as ET


def getMissions(data):
    cfg = get_config()

    r = requests.post(cfg['cmr_base'] + cfg['cmr_collections'], headers=cfg['cmr_headers'], data=data)
    if r.status_code != 200:
        return { 'errors': [{'type': 'CMR_ERROR', 'report': 'CMR Error: {0}'.format(r.text)}]}

    try:
        root = ET.fromstring(r.text.encode('latin-1'))
    except ET.ParseError as e:
        return {'errors': [{'type': 'CMR_ERROR', 'report': 'Error parsing XML from CMR: {0}'.format(e)}]}

    missions = [f.text for f in root.findall('.//facets/facet[@field="project"]/value')]
    missions = sorted(missions, key=lambda s: s.casefold())
    logging.debug(missions)

    # All done
    return { 'result': missions }
