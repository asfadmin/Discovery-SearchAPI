from flask import Flask, make_response
from flask import request
from flask import Response
from APIProxy import APIProxyQuery
from WKTValidator import WKTValidator
from FilesToWKT import FilesToWKT
from MissionList import MissionList
from datetime import datetime
from urllib import parse
import sys
import logging
import os
import requests
import json
from CacheQuery import response_from_cache
from CMR.Health import get_cmr_health

# EB looks for an 'application' callable by default.
application = Flask(__name__)

########## Bulk Download API endpoints and support ##########

# Read a blank download script, populate it with product URLs if needed
def create_script():
    with open('bulk_download.py', 'r') as script_file:
        script = script_file.read()

    # need to move these to external config
    script = script.replace('REPLACE_URS_URL', 'https://urs.earthdata.nasa.gov/oauth/authorize')
    script = script.replace('REPLACE_CLIENT_ID', 'BO_n7nTIlMljdvU6kRRB3g')
    script = script.replace('REPLACE_REDIR_URL', 'https://vertex.daac.asf.alaska.edu/services/urs4_token_request')
    script = script.replace('REPLACE_HELP_URL', 'http://bulk-download.asf.alaska.edu/help')

    filename = get_filename()
    script = script.replace('REPLACE_FILENAME', filename)

    products = None
    try:
        products = request.values.getlist('products')
        all_products = []
        for p in products:
            all_products += parse.unquote(p).split(',')
        products = list(filter(lambda p: p is not None, map(lambda p: ('"' + str(p) + '"') if p else None, all_products)))
    except:
        products = []
    script = script.replace('\'REPLACE_PRODUCT_LIST\'', ",\n                       ".join(products))
    return script

# Returns either the default filename or the param-specified one
def get_filename():
    if 'filename' in request.values:
        return request.values['filename']
    return 'download-all-{0}.py'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

# Posts a pageview to google universal analytics
def post_analytics():
    url = "http://www.google-analytics.com/collect"
    params = {
        "v":    "1",
        "tid":  "UA-116306456-1",
        "cid":  "555",
        "t":    "pageview",
        "uip":  request.access_route[-1],
        "dr":   request.referrer,
        "dl":   request.url}

    r = requests.post(url, data = params)

# Send the help docs
@application.route('/help')
def view_help():
    post_analytics()
    return application.send_static_file('./help.html')

# Send the generated script as content formatted for display in the browser
@application.route('/view')
def view_script():
    post_analytics()
    return '<html><pre>' + create_script() + '</pre></html>'

# Send the generated script as an attachment so it downloads directly
@application.route('/', methods = ['GET', 'POST'])
def get_script():
    post_analytics()
    filename = get_filename()
    results = create_script()
    generator = (cell for row in results
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
    return APIProxyQuery(request).get_response()

# Fetch results from the jsonlite_cache
@application.route('/services/search/cache', methods= ['GET', 'POST'])
def read_cache():
    return response_from_cache(request)

########## General endpoints ##########

# Health check endpoint
@application.route('/health')
def health_check():
    cmr_health = get_cmr_health()
    api_health = {'ASFSearchAPI': {'ok?': True}, 'CMRSearchAPI': cmr_health}
    return make_response(json.dumps(api_health, sort_keys=True, indent=2))
    return make_response("I am putting myself to the fullest possible use, which is all I think that any conscious entity can ever hope to do.")

@application.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# Run a dev server
if __name__ == '__main__':
    if 'MATURITY' not in os.environ:
        os.environ['MATURITY'] = 'dev'
    sys.dont_write_bytecode = True  # prevent clutter
    application.debug = True        # enable debugging mode
    FORMAT = "[%(filename)18s:%(lineno)-4s - %(funcName)18s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT) # enable debugging output
    application.run(threaded=True)  # run threaded to prevent a broken pipe error
