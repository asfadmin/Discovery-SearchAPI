import os
import logging
from flask import request

def get_config():
    if 'MATURITY' not in os.environ.keys():
        logging.warning('os.environ[\'MATURITY\'] not set! Defaulting to local config.]')
    maturity = os.environ['MATURITY'] if 'MATURITY' in os.environ.keys() else 'local'

    maturities = get_maturities()

    if maturities[maturity]['flexible_maturity'] and hasattr(request, 'temp_maturity'):
        maturity = request.temp_maturity

    return maturities[maturity]

def get_maturities():
    return {
        'local': {
            'this_api': 'http://local.asf.alaska.edu:5000',
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': None,
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
            'this_api': 'https://api-dev.asf.alaska.edu',
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-4',
            'cmr_base': 'https://cmr.uat.earthdata.nasa.gov',
            'cmr_health': '/search/health',
            'cmr_api': '/search/granules.echo10',
            'cmr_collections': '/search/collections',
            'cmr_headers': {
                'Client-Id': 'vertex_asf'
            },
            'flexible_maturity': True
        },
        'devel-beanstalk': {
            'this_api': 'https://api-dev.asf.alaska.edu',
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-4',
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
            'this_api': 'https://api-test.asf.alaska.edu',
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-3',
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
            'this_api': 'https://api-test.asf.alaska.edu',
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-3',
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
            'this_api': 'https://api.daac.asf.alaska.edu',
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-2',
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
            'this_api': 'https://api-prod-private.asf.alaska.edu',
            'bulk_download_api': 'https://bulk-download.asf.alaska.edu',
            'analytics_id': 'UA-118881300-5',
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
