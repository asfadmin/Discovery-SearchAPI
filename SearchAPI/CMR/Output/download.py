import logging
import requests
from SearchAPI.asf_env import get_config

def req_fields_download():
    fields = [
        'downloadUrl',
    ]
    return fields

def cmr_to_download(rgen, includeBaseline=False, addendum=None):
    logging.debug('translating: bulk download script')
    plist = [p['downloadUrl'] for p in rgen()]
    bd_res = requests.post(get_config()['bulk_download_api'], data={'products': ','.join(plist)})

    yield bd_res.text
