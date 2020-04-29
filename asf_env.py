import os
import logging
from flask import request

def get_config():
    if 'MATURITY' not in os.environ.keys():
        logging.warning('os.environ[\'MATURITY\'] not set! Defaulting to local config.]')

    maturity = os.environ['MATURITY'] if 'MATURITY' in os.environ.keys() else 'local'
    maturities = get_maturities()

    # need to inject this into the temporary maturity for crossover to prod so it still accepts the 'maturity' param
    flex_maturity = maturities[maturity]['flexible_maturity']

    if maturities[maturity]['flexible_maturity'] and hasattr(request, 'temp_maturity'):
        maturity = request.temp_maturity

    config = maturities[maturity]
    config['flexible_maturity'] = flex_maturity

    return config

def get_maturities():
    return {
        'local': {
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': None,
            'this_api': 'http://127.0.0.1:5000',
            'cmr_base': 'https://cmr.earthdata.nasa.gov',
            'cmr_health': '/search/health',
            'cmr_api': '/search/granules.echo10',
            'cmr_collections': '/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            },
            'flexible_maturity': True
        },
        'devel': {
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-4',
            'this_api': 'https://api-dev.asf.alaska.edu',
            'cmr_base': 'https://cmr.uat.earthdata.nasa.gov',
            'cmr_health': '/search/health',
            'cmr_api': '/search/granules.echo10',
            'cmr_collections': '/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_alocal.asf.alaska.edusf'
            },
            'flexible_maturity': True
        },
        'devel-beanstalk': {
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-4',
            'this_api': 'https://api-dev-beanstalk.asf.alaska.edu',
            'cmr_base': 'https://cmr.uat.earthdata.nasa.gov',
            'cmr_health': '/search/health',
            'cmr_api': '/search/granules.echo10',
            'cmr_collections': '/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            },
            'flexible_maturity': True
        },
        'test': {
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-3',
            'this_api': 'https://api-test.asf.alaska.edu',
            'cmr_base': 'https://cmr.uat.earthdata.nasa.gov',
            'cmr_health': '/search/health',
            'cmr_api': '/search/granules.echo10',
            'cmr_collections': '/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            },
            'flexible_maturity': True
        },
        'test-beanstalk': {
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-3',
            'this_api': 'https://api-test-beanstalk.asf.alaska.edu',
            'cmr_base': 'https://cmr.uat.earthdata.nasa.gov',
            'cmr_health': '/search/health',
            'cmr_api': '/search/granules.echo10',
            'cmr_collections': '/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            },
            'flexible_maturity': True
        },
        'prod': {
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': None,
            'this_api': 'https://api.daac.asf.alaska.edu',
            'cmr_base': 'https://cmr.earthdata.nasa.gov',
            'cmr_health': '/search/health',
            'cmr_api': '/search/granules.echo10',
            'cmr_collections': '/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            },
            'flexible_maturity': False
        },
        'prod-private': {
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-5',
            'this_api': 'https://api-prod-private.asf.alaska.edu',
            'cmr_base': 'https://cmr.earthdata.nasa.gov',
            'cmr_health': '/search/health',
            'cmr_api': '/search/granules.echo10',
            'cmr_collections': '/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            },
            'flexible_maturity': False
        }
    }
