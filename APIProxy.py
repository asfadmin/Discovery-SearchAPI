from flask import Response
import requests
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

class APIProxyQuery:
    
    def __init__(self, request):
        self.request = request  # store the incoming request
        
    def can_use_cmr(self):
        return False
    
    def get_response(self):
        if self.can_use_cmr():
            logging.debug('get_response(): using CMR backend')
            return self.query_cmr()
        logging.debug('get_response(): using ASF backend')
        return self.query_asf()

    def query_asf(self):
        logging.info('API passthrough from {0} with params {1}'.format(self.request.access_route[-1], self.request.query_string))
        r = requests.get('https://api.daac.asf.alaska.edu/services/search/param?api_proxy=1&{0}'.format(self.request.query_string.decode("utf-8")))
        if r.status_code != 200:
            logging.warning('Received status_code {0} from ASF API with params {1}'.format(r.status_code, self.request.query_string.decode("utf-8")))
        return Response(r.text, r.status_code, r.headers.items())
    
    def query_cmr(self):
        logging.info('CMR translation from {0} with params {1}'.format(self.request.access_route[-1], self.request.query_string))
        
        return Response('I wish')
