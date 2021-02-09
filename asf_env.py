import os
import logging
import yaml
from flask import request

def load_config():
    with open("maturities.yml", "r") as yml_file:
        all_config = yaml.safe_load(yml_file)

    if 'MATURITY' not in os.environ.keys():
        logging.warning('os.environ[\'MATURITY\'] not set! Defaulting to local config.]')

    maturity = os.environ['MATURITY'] if 'MATURITY' in os.environ.keys() else 'local'

    config = all_config[maturity]

    if config['flexible_maturity']:
        if 'maturity' in request.values:
            temp_maturity = request.values['maturity']
            request.temp_maturity = temp_maturity
            for flex_key in ['bulk_download_api', 'cmr_base', 'cmr_health', 'cmr_api', 'cmr_collections']:
                config[flex_key] = all_config[temp_maturity][flex_key]
            del request.values['maturity']
            if 'cmr_token' in request.values:
                request.cmr_token = request.values['cmr_token']
            del request.values['cmr_token']
            if 'cmr_provider' in request.values:
                request.cmr_provider = request.values['cmr_provider']
            del request.values['cmr_provider']

    # dynamically switch to non-scrolled results if the max results <= page size
    if 'maxresults' in request.values:
        try:
            if int(request.values['maxresults']) <= config['cmr_page_size']:
                config['cmr_scroll'] = False
        except ValueError:
            pass

    if 'granule_list' in request.values or 'product_list' in request.values:
        config['cmr_scroll'] = False

    request.asf_config = config
    request.asf_base_maturity = maturity

def get_config():
    return request.asf_config
