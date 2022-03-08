import os
import logging
import yaml
from flask import request

def load_config_file():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),  "maturities.yml")
    with open(file_path, "r", encoding='utf-8') as yml_file:
        config = yaml.safe_load(yml_file)
    return config

def load_config():
    all_config = load_config_file()

    if 'MATURITY' not in os.environ.keys():
        logging.warning('os.environ[\'MATURITY\'] not set! Defaulting to local config.]')

    maturity = os.environ['MATURITY'] if 'MATURITY' in os.environ.keys() else 'local'

    config = all_config[maturity]
    request.local_values = request.values.to_dict()
    if config['flexible_maturity']:
        if 'maturity' in request.local_values:
            temp_maturity = request.local_values['maturity']
            request.temp_maturity = temp_maturity
            del request.local_values['maturity']
            for flex_key in ['bulk_download_api', 'cmr_base', 'cmr_health', 'cmr_api', 'cmr_collections']:
                config[flex_key] = all_config[temp_maturity][flex_key]
            if 'cmr_token' in request.local_values:
                request.cmr_token = request.local_values['cmr_token']
                del request.local_values['cmr_token']
            if 'cmr_provider' in request.local_values:
                request.cmr_provider = request.local_values['cmr_provider']
                del request.local_values['cmr_provider']

    request.asf_config = config
    request.asf_base_maturity = maturity

def get_config():
    return request.asf_config
