from flask import Flask, make_response
from flask import request
from flask import Response
from flask_talisman import Talisman
from flask_cors import CORS
from SearchQuery import APISearchQuery
from StackQuery import APIStackQuery
from urllib import parse
import sys
import logging
import os
import json
from CMR.Health import get_cmr_health
from Analytics import analytics_pageview
from werkzeug.exceptions import RequestEntityTooLarge
import multiprocessing
import requests
from asf_env import get_config, load_config
from time import perf_counter
import boto3

import endpoints

application = Flask(__name__)
application.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # limit to 10 MB, primarily affects file uploads
CORS(application, send_wildcard=True)
talisman = Talisman(application)


def get_product_list():
    products = None
    try:
        products = request.local_values.getlist('products')
        all_products = []
        for p in products:
            all_products += parse.unquote(p).split(',')
        products = list(filter(lambda p: p is not None, map(lambda p: ('"' + str(p) + '"') if p else None, all_products)))
    except:
        products = []
    return products


########## Search API endpoints ##########

# Validate and/or repair a WKT to ensure it meets CMR's requirements
@application.route('/services/utils/wkt', methods = ['GET', 'POST'])
def validate_wkt():
    return endpoints.RepairWKT_Endpoint(request).get_response()

# Validate a date to ensure it meets our requirements
@application.route('/services/utils/date', methods = ['GET', 'POST'])
def validate_date():
    return endpoints.DateValidator_Endpoint(request).get_response()

# Convert a set of shapefiles or a geojson file to WKT
@application.route('/services/utils/files_to_wkt', methods = ['POST'])
def filesToWKT():
    return endpoints.FilesToWKT_Endpoint(request).get_response()

# Collect a list of missions from CMR for a given platform
@application.route('/services/utils/mission_list', methods = ['GET', 'POST'])
def missionList():
    return endpoints.MissionList_Endpoint(request).get_response()

# Fetch and convert the results from CMR
@application.route('/services/search/param', methods = ['GET', 'POST'])
def proxy_search():
    return APISearchQuery(request, should_stream=True).get_response()

@application.route('/services/load/param', methods = ['GET', 'POST'])
def proxy_search_without_stream():
    return APISearchQuery(request, should_stream=False).get_response()

@application.route('/services/search/baseline', methods = ['GET', 'POST'])
def stack_search():
    return APIStackQuery(request).get_response()


########## General endpoints ##########

# Health check endpoint
@application.route('/')
@application.route('/health')
@talisman(force_https=False)
def health_check():
    try:
        with open('version.json') as version_file:
            api_version = json.load(version_file)
    except Exception as e:
        logging.debug(e)
        api_version = {'version': 'unknown'}
    cmr_health = get_cmr_health()
    api_health = {'ASFSearchAPI': {'ok?': True, 'version': api_version['version'], 'config': request.asf_config}, 'CMRSearchAPI': cmr_health}
    response = make_response(json.dumps(api_health, sort_keys=True, indent=2))
    response.mimetype = 'application/json; charset=utf-8'
    return response

# Send the API swagger docs
@application.route('/reference')
def reference():
    return application.send_static_file('./SearchAPIRef.yaml')

########## Helper functionality ##########

@application.errorhandler(RequestEntityTooLarge)
def handle_oversize_request(error):
    resp = Response(json.dumps({'errors': [{'type': 'VALUE', 'report': 'Selected file is too large.'}] }, sort_keys=True, indent=2), status=413, mimetype='application/json')
    return resp

# Pre-flight operations
@application.before_request
def preflight():
    load_config()
    analytics_pageview()
    request.cmr_scroll_sessions = []
    logging.debug('Using config:')
    logging.debug(get_config())
    request.query_start_time = perf_counter()

# Post-flight operations
@application.teardown_request
def postflight(e):
    def close_cmr_scroll(req):
        try:
            logging.debug(f'Closing CMR scroll session {req["sid"]}')
            r = requests.post(req['url'], json={'scroll_id': req['sid']})
            if r.ok:
                logging.debug(f'Closed session {req["sid"]}')
            else:
                logging.warning(f'CMR returned HTTP {r.status_code} when closing scroll session {req["sid"]}')
        except Exception as e:
            logging.warning(f'Failed to close scroll session {req["sid"]}: {e}')

    try:
        query_run_time = perf_counter() - request.query_start_time
        logging.debug(f'Total query run time: {query_run_time}')
        if request.asf_config['cloudwatch_metrics']:
            logging.debug('Logging query run time to cloudwatch metrics')
            cloudwatch = boto3.client('cloudwatch')
            response = cloudwatch.put_metric_data(
                MetricData = [
                    {
                        'MetricName': 'TotalQueryRunTime',
                        'Dimensions': [
                            {
                                'Name': 'maturity',
                                'Value': request.asf_base_maturity
                            }
                        ],
                        'Unit': 'None',
                        'Value': query_run_time
                    }
                ],
                Namespace = 'SearchAPI'
            )

        logging.debug(f'Closing {len(request.cmr_scroll_sessions)} scroll sessions')
        if len(request.cmr_scroll_sessions) > 0:
            num_processes = min([4, len(request.cmr_scroll_sessions)])
            p = multiprocessing.pool.ThreadPool(processes=num_processes)
            reqs = [{'sid': sid, 'url': get_config()['cmr_base']+get_config()['cmr_clear_scroll']} for sid in request.cmr_scroll_sessions]
            p.map_async(close_cmr_scroll, reqs)
            p.close()
            p.join()
    except Exception as e:
        logging.critical(f'Failure during request teardown: {e}')

# Run a dev server
if __name__ == '__main__':
    if 'MATURITY' not in os.environ:
        os.environ['MATURITY'] = 'local'
    sys.dont_write_bytecode = True  # prevent clutter
    application.debug = True        # enable debugging mode
    FORMAT = "[%(filename)18s:%(lineno)-4s - %(funcName)18s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT) # enable debugging output
    application.run(threaded=True)  # run threaded to prevent a broken pipe error
