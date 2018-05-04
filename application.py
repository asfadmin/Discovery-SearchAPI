from flask import Flask
from flask import request
from APIProxy import APIProxy

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# Send the generated script as an attachment so it downloads directly
@application.route('/services/search/param', methods = ['GET', 'POST'])
def proxy_search():
    application.logger.debug('API passthrough from {0} with params {1}'.format(request.access_route[-1], request.query_string))
    api = APIProxy(request)
    return api.get_response()

# run the app
if __name__ == '__main__':
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    #app.debug = True
    application.run(threaded=True)
