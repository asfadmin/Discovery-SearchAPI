from flask import Flask, make_response
import serverless_wsgi
from flask import request
from flask import Response
from flask_talisman import Talisman
from flask_cors import CORS
from SearchAPI.SearchQuery import APISearchQuery
from SearchAPI.StackQuery import APIStackQuery
from urllib import parse
import sys
import logging
import os
import json
from SearchAPI.CMR.Health import get_cmr_health
from SearchAPI.CMR.Output import output_translators
from SearchAPI.Analytics import analytics_pageview
from werkzeug.exceptions import RequestEntityTooLarge
from SearchAPI.asf_env import get_config, load_config
from time import perf_counter
import boto3

import SearchAPI.endpoints as endpoints

application = Flask(__name__)
application.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # limit to 10 MB, primarily affects file uploads
CORS(application, send_wildcard=True)
talisman = Talisman(application)

# So this isn't repeated with each call to the lambda hook:
file_outputs = output_translators()
for _, file in file_outputs.items():
    mimetype = file[1]
    mimetype = mimetype.split(';')[0] if ";" in mimetype else mimetype
    serverless_wsgi.TEXT_MIME_TYPES.append(mimetype)


def get_product_list():
    products = None
    try:
        products = request.local_values.getlist('products')
        all_products = []
        for p in products:
            all_products += parse.unquote(p).split(',')
        products = list(filter(lambda p: p is not None, map(lambda p: ('"' + str(p) + '"') if p else None, all_products)))
    except Exception:
        products = []
    return products


########## Search API endpoints ##########

# Validate and/or repair a WKT to ensure it meets CMR's requirements
@application.route('/services/utils/wkt', methods = ['GET', 'POST'])
@talisman(force_https=False)
def validate_wkt():
    return endpoints.RepairWKT_Endpoint(request).get_response()

# Validate a date to ensure it meets our requirements
@application.route('/services/utils/date', methods = ['GET', 'POST'])
@talisman(force_https=False)
def validate_date():
    return endpoints.DateValidator_Endpoint(request).get_response()

# Convert a set of shapefiles or a geojson file to WKT
@application.route('/services/utils/files_to_wkt', methods = ['POST'])
@talisman(force_https=False)
def filesToWKT():
    return endpoints.FilesToWKT_Endpoint(request).get_response()

# Collect a list of missions from CMR for a given platform
@application.route('/services/utils/mission_list', methods = ['GET', 'POST'])
@talisman(force_https=False)
def missionList():
    return endpoints.MissionList_Endpoint(request).get_response()

# Fetch and convert the results from CMR
@application.route('/services/search/param', methods = ['GET', 'POST'])
@talisman(force_https=False)
def proxy_search():
    return APISearchQuery(request, should_stream=True).get_response()

@application.route('/services/load/param', methods = ['GET', 'POST'])
@talisman(force_https=False)
def proxy_search_without_stream():
    return APISearchQuery(request, should_stream=False).get_response()

@application.route('/services/search/baseline', methods = ['GET', 'POST'])
@talisman(force_https=False)
def stack_search():
    return APIStackQuery(request).get_response()


########## General endpoints ##########

# Health check endpoint
@application.route('/')
@application.route('/health')
@talisman(force_https=False)
def health_check():
    try:
        version_path = os.path.join("SearchAPI", "version.json")
        with open(version_path, 'r', encoding="utf-8") as version_file:
            api_version = json.load(version_file)
    except Exception as e:
        logging.debug(e)
        api_version = {'version': 'unknown'}
    cmr_health = get_cmr_health()
    api_health = {'ASFSearchAPI': {'ok?': True, 'version': api_version['version'], 'config': request.asf_config}, 'CMRSearchAPI': cmr_health}
    response = make_response(json.dumps(api_health, sort_keys=True, indent=2))
    response.mimetype = 'application/json; charset=utf-8'
    return response

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
    logging.debug('Using config:')
    logging.debug(get_config())
    request.query_start_time = perf_counter()

# Post-flight operations
@application.teardown_request
def postflight(e):
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
    except Exception as e:
        logging.critical(f'Failure during request teardown: {e}')

# Lambda hook, to run in AWS:
def run_flask_lambda(event, context):
    return serverless_wsgi.handle_request(application, event, context)

# So you can call this from the Dockerfile as well:
## NOTE: This'll be called by the container too. We can't JUST have it be debug by default
def run_flask():
    # Make sure maturity is set, and you're not debugging on prod:
    if 'MATURITY' not in os.environ:
        os.environ['MATURITY'] = 'local'
    if "prod" not in os.environ["MATURITY"].lower():
        application.debug = True

    if 'OPEN_TO_IP' not in os.environ:
        os.environ['OPEN_TO_IP'] = '127.0.0.1'

    sys.dont_write_bytecode = True  # prevent clutter
    FORMAT = "[%(filename)18s:%(lineno)-4s - %(funcName)18s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT) # enable debugging output
    application.run(threaded=True, host=os.environ['OPEN_TO_IP'], port=80)  # run threaded to prevent a broken pipe error

# Run a dev server
if __name__ == '__main__':
    run_flask()
