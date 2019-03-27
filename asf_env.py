import os
import logging

def get_config():
    if 'MATURITY' not in os.environ.keys():
        logging.warning('os.environ[\'MATURITY\'] not set! Defaulting to prod config.]')
    return {
        'dev': {
            'bulk_download_api': 'https://bulk-download-test.asf.alaska.edu',
            'analytics_id': 'UA-118881300-4',
            'cmr_api': 'https://cmr.earthdata.nasa.gov/search/granules.echo10',
            'cmr_collections': 'https://cmr.earthdata.nasa.gov/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            }
        },
        'test': {
            'bulk_download_api': 'https://bulk-download-test.asf.alaska.edu',
            'analytics_id': 'UA-118881300-3',
            'cmr_api': 'https://cmr.uat.earthdata.nasa.gov/search/granules.echo10',
            'cmr_collections': 'https://cmr.uat.earthdata.nasa.gov/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            }
        },
        'prod': {
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-2',
            'cmr_api': 'https://cmr.earthdata.nasa.gov/search/granules.echo10',
            'cmr_collections': 'https://cmr.earthdata.nasa.gov/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            }
        }
    }[os.environ['MATURITY'] if 'MATURITY' in os.environ.keys() else 'prod']
