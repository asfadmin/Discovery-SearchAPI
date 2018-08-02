import os
import logging

def get_config():
    if 'MATURITY' not in os.environ.keys():
        logging.warning('os.environ[\'MATURITY\'] not set! Defaulting to prod config.]')
    return {
        'dev': {
            'cmr_api': 'https://cmr.earthdata.nasa.gov/search/granules.echo10',
            'bulk_download_api': 'https://bulk-download-test.asf.alaska.edu',
            'analytics_id': 'UA-118881300-4'
        },
        'test': {
            'cmr_api': 'https://cmr.earthdata.nasa.gov/search/granules.echo10',
            'bulk_download_api': 'https://bulk-download-test.asf.alaska.edu',
            'analytics_id': 'UA-118881300-3'
        },
        'prod': {
            'cmr_api': 'https://cmr.earthdata.nasa.gov/search/granules.echo10',
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-2'
        }
    }[os.environ['MATURITY'] if 'MATURITY' in os.environ.keys() else 'prod']