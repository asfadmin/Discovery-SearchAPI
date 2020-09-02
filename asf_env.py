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
    maturities = all_config

    # need to inject this into the temporary maturity for crossover to prod so it still accepts the 'maturity' param
    flex_maturity = maturities[maturity]['flexible_maturity']

    if maturities[maturity]['flexible_maturity'] and hasattr(request, 'temp_maturity'):
        maturity = request.temp_maturity

    config = maturities[maturity]
    config['flexible_maturity'] = flex_maturity

    # dynamically switch to non-scrolled results if the max results <= page size
    if 'maxresults' in request.values:
        try:
            if int(request.values['maxresults']) <= config['cmr_page_size']:
                config['cmr_scroll'] = False
        except ValueError:
            pass

    request.asf_config = config
    logging.debug('====================')
    logging.debug(request.asf_config)

def get_config():
    return request.asf_config
