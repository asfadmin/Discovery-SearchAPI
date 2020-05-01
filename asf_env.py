import os
import logging
import yaml
from flask import request

def load_config():
    with open("maturities.yml", "r") as yml_file:
        request.asf_config = yaml.safe_load(yml_file)

def get_config():
    if 'MATURITY' not in os.environ.keys():
        logging.warning('os.environ[\'MATURITY\'] not set! Defaulting to local config.]')

    maturity = os.environ['MATURITY'] if 'MATURITY' in os.environ.keys() else 'local'
    maturities = request.asf_config

    # need to inject this into the temporary maturity for crossover to prod so it still accepts the 'maturity' param
    flex_maturity = maturities[maturity]['flexible_maturity']

    if maturities[maturity]['flexible_maturity'] and hasattr(request, 'temp_maturity'):
        maturity = request.temp_maturity

    config = maturities[maturity]
    config['flexible_maturity'] = flex_maturity

    return config
