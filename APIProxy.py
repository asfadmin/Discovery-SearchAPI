from flask import Response
import requests
import logging
from flask.logging import default_handler

class APIProxy(object):
    
    def __init__(self, request):
        self.log = logging.getLogger()
        self.log.addHandler(default_handler)
        self.request = request

    def get_response(self):
        self.log.debug('API passthrough from {0} with params {1}'.format(self.request.access_route[-1], self.request.query_string))
        r = requests.get('https://api.daac.asf.alaska.edu/services/search/param?api_proxy=1&{0}'.format(self.request.query_string))
        if r.status_code != 200:
            self.log.warning('Received status_code {0} from ASF API with params {1}'.format(r.status_code, self.request.query_string))
        return Response(r.text, r.status_code, r.headers.items())