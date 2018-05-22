from flask import Flask, make_response
from flask import request
from APIProxy import APIProxyQuery
import sys
import logging
import os

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# Either get the results from CMR, or pass the query through to the legacy API
@application.route('/services/search/param', methods = ['GET', 'POST'])
def proxy_search():
    return APIProxyQuery(request).get_response()

# Health check endpoint
@application.route('/health')
def health_check():
    return make_response("I am putting myself to the fullest possible use, which is all I think that any conscious entity can ever hope to do.")

# Run a dev server
if __name__ == '__main__':
    if 'MATURITY' not in os.environ:
        os.environ['MATURITY'] = 'dev'
    sys.dont_write_bytecode = True  # prevent clutter
    application.debug = True        # enable debugging mode
    logging.basicConfig(level=logging.DEBUG) # enable debugging output
    application.run(threaded=True)  # run threaded to prevent a broken pipe error
