from flask import Flask, make_response
from flask import request
from flask import Response
from flask_compress import Compress
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
import time
import urllib
import importlib
from asf_env import get_config

import endpoints


project_root = os.path.dirname(os.path.abspath(__file__))
bulk_download_repo = "Discovery-BulkDownload"
# Submodule imports:
sys.path.append(os.path.join(project_root, bulk_download_repo))
BulkDownloadAPI = importlib.import_module("APIBulkDownload")
sys.path.remove(os.path.join(project_root, bulk_download_repo))

application = Flask(__name__)
application.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # limit to 10 MB, primarily affects file uploads
CORS(application)
Compress(application)
talisman = Talisman(application)

########## Bulk Download API endpoints and support ##########
config = {
    'urs_url': 'https://urs.earthdata.nasa.gov/oauth/authorize',
    'client_id': 'BO_n7nTIlMljdvU6kRRB3g',
    'redir_url': 'https://auth.asf.alaska.edu/login',
    'help_url': 'http://bulk-download.asf.alaska.edu/help'
}

# Returns either the default filename or the param-specified one
def get_filename():
    if 'filename' in request.values:
        return request.values['filename']
    return BulkDownloadAPI.get_default_filename()

def get_product_list():
    products = None
    try:
        products = request.values.getlist('products')
        all_products = []
        for p in products:
            all_products += parse.unquote(p).split(',')
        products = list(filter(lambda p: p is not None, map(lambda p: ('"' + str(p) + '"') if p else None, all_products)))
    except:
        products = []
    return products

# Send the help docs
@application.route('/help')
def view_help():
    return application.send_static_file('./help.html')

# Send the generated script as content formatted for display in the browser
@application.route('/view')
def view_script():
    return '<html><pre>' + BulkDownloadAPI.create_script(config=config, filename=get_filename(), products=get_product_list()) + '</pre></html>'

# Send the generated script as an attachment so it downloads directly
@application.route('/', methods = ['GET', 'POST'])
def get_script():
    filename = get_filename()
    results = BulkDownloadAPI.create_script(config=config, filename=filename, products=get_product_list())
    generator = (cell for row in results
                    for cell in row)
    return Response(generator,
                       mimetype = 'text/plain',
                       headers = {'Content-Disposition':
                                  'attachment;filename=' + filename})

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
    api_health = {'ASFSearchAPI': {'ok?': True, 'version': api_version['version']}, 'CMRSearchAPI': cmr_health}
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
    analytics_pageview()
    if get_config()['flexible_maturity']:
        if 'maturity' in request.values:
            request.temp_maturity = request.values['maturity']

# Run a dev server
if __name__ == '__main__':
    if 'MATURITY' not in os.environ:
        os.environ['MATURITY'] = 'local'
    sys.dont_write_bytecode = True  # prevent clutter
    application.debug = True        # enable debugging mode
    FORMAT = "[%(filename)18s:%(lineno)-4s - %(funcName)18s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT) # enable debugging output
    application.run(threaded=True)  # run threaded to prevent a broken pipe error
