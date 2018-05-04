from flask import Flask
from flask import request
from APIProxy import APIProxy
import sys

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# Send the generated script as an attachment so it downloads directly
@application.route('/services/search/param', methods = ['GET', 'POST'])
def proxy_search():
    api = APIProxy(request)
    return api.get_response()

# run the app
if __name__ == '__main__':
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.logger.warning('we are in main!')
    sys.dont_write_bytecode = True
    application.debug = True
    application.run(threaded=True)
