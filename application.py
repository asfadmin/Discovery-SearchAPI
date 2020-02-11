from flask import Flask, make_response
from flask import request
from flask import Response
from flask_compress import Compress
from APIProxy import APIProxyQuery
from WKTValidator import WKTValidator
from DateValidator import DateValidator
from FilesToWKT import FilesToWKT
from MissionList import MissionList
from datetime import datetime
from urllib import parse
import sys
import logging
import os
import json
from CMR.Health import get_cmr_health
from Analytics import analytics_pageview
from werkzeug.exceptions import RequestEntityTooLarge
import time
import importlib

# GLOBALS:
project_root = os.path.dirname(os.path.abspath(__file__))
bulk_download_repo = "Discovery-BulkDownload"
utils_api_repo = "Discovery-UtilsAPI"

# Submodule imports:
sys.path.append(os.path.join(project_root, bulk_download_repo))
BulkDownloadAPI = importlib.import_module("APIBulkDownload")
sys.path.remove(os.path.join(project_root, bulk_download_repo))

# sys.path.append(os.path.join(project_root, utils_api_repo))
# UtilsAPI = importlib.import_module("APIBulkDownload")
# sys.path.remove(os.path.join(project_root, utils_api_repo))

# EB looks for an 'application' callable by default.
application = Flask(__name__)
Compress(application)
application.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # limit to 10 MB, primarily affects file uploads

########## Bulk Download API endpoints and support ##########

def get_products():
    try:
        products = request.values.getlist('products')
        all_products = []
        for p in products:
            all_products += parse.unquote(p).split(',')
        products = list(filter(lambda p: p is not None, map(lambda p: ('"' + str(p) + '"') if p else None, all_products)))
    except:
        products = []
    return products

def get_filename():
    if "filename" in request.values:
        return request.values["filename"]
    return BulkDownloadAPI.get_default_filename()

# Send the help docs
@application.route('/help')
def view_help():
    return application.send_static_file('./help.html')

# Send the generated script as content formatted for display in the browser
@application.route('/view')
def view_script():
    filename = get_filename()
    products = get_products()
    return '<html><pre>' + BulkDownloadAPI.create_script(filename, products) + '</pre></html>'

# Send the generated script as an attachment so it downloads directly
@application.route('/', methods = ['GET', 'POST'])
def get_script():
    filename = get_filename()
    products = get_products()
    script = BulkDownloadAPI.create_script(filename, products)
    generator = (cell for row in script
                    for cell in row)
    return Response(generator,
                       mimetype = 'text/plain',
                       headers = {'Access-Control-Allow-Origin': '*',
                                  'Content-Disposition':
                                  'attachment;filename=' + filename})

########## Search API endpoints ##########

# Validate and/or repair a WKT to ensure it meets CMR's requirements
@application.route('/services/utils/wkt', methods = ['GET', 'POST'])
def validate_wkt():
    return WKTValidator(request).get_response()

# Validate a date to ensure it meets our requirements
@application.route('/services/utils/date', methods = ['GET', 'POST'])
def validate_date():
    return DateValidator(request).get_response()

# Convert a set of shapefiles or a geojson file to WKT
@application.route('/services/utils/files_to_wkt', methods = ['POST'])
def filesToWKT():
    return FilesToWKT(request).get_response()

# Collect a list of missions from CMR for a given platform
@application.route('/services/utils/mission_list', methods = ['GET', 'POST'])
def missionList():
    return MissionList(request).get_response()

# Fetch and convert the results from CMR
@application.route('/services/search/param', methods = ['GET', 'POST'])
def proxy_search():
    return APIProxyQuery(request, should_stream=True).get_response()


@application.route('/services/load/param', methods = ['GET', 'POST'])
def proxy_search_without_stream():
    return APIProxyQuery(request, should_stream=False).get_response()


########## General endpoints ##########

# Health check endpoint
@application.route('/health')
def health_check():
    cmr_health = get_cmr_health()
    api_health = {'ASFSearchAPI': {'ok?': True}, 'CMRSearchAPI': cmr_health}
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
    resp = Response(json.dumps({'error': {'type': 'VALUE', 'report': 'Selected file is too large.'} }, sort_keys=True, indent=2), status=413, mimetype='application/json')
    return resp

# Pre-flight operations
@application.before_request
def preflight():
    #request.asf_start_proc_time = time.process_time()
    #request.asf_start_real_time = time.perf_counter()
    analytics_pageview()

# Cleanup operations
@application.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

'''
@application.teardown_request
def postflight(exc):
    try:
        if exc is not None:
            logging.error('Postflight handler encountered exception: {0}'.format(exc))
        end_proc_time = time.process_time()
        total_proc_time = end_proc_time - request.asf_start_proc_time
        end_real_time = time.perf_counter()
        total_real_time = end_real_time - request.asf_start_real_time
        #if total_proc_time / total_real_time > .5 or total_real_time > 10:
        # process time (s), real time (s), proc/real time ratio, URL, params
        logging.warning('Request timing analysis: {0}, {1}, {2}, {3}, {4}'.format(total_proc_time, total_real_time, total_proc_time / total_real_time, request.url, request.values))
    except Exception as e:
        logging.error('Exception encountered in postflight handler: {0}'.format(e))
'''

# Run a dev server
if __name__ == '__main__':
    if 'MATURITY' not in os.environ:
        os.environ['MATURITY'] = 'dev'
    sys.dont_write_bytecode = True  # prevent clutter
    application.debug = True        # enable debugging mode
    FORMAT = "[%(filename)18s:%(lineno)-4s - %(funcName)18s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT) # enable debugging output
    application.run(threaded=True)  # run threaded to prevent a broken pipe error
