from flask import Flask
from flask import request
from APIProxy import APIProxyQuery
import sys
import logging

# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.logger.setLevel(logging.INFO)

# Either get the results from CMR, or pass the query through to the legacy API
@application.route('/services/search/param', methods = ['GET', 'POST'])
def proxy_search():
    api = APIProxyQuery(request)
    return api.get_response()

# Run a dev server
if __name__ == '__main__':
    sys.dont_write_bytecode = True  # prevent clutter
    application.debug = True        # enable debugging mode
    application.logger.setLevel(logging.DEBUG) # enable debugging output
    application.run(threaded=True)  # run threaded to prevent a broken pipe error
