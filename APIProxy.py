from flask import Response
import requests

class APIProxy(object):
    
    def __init__(self, request):
        self.request = request

    def get_response(self):
        r = requests.get('https://api.daac.asf.alaska.edu/services/search/param?api_proxy=1&{0}'.format(self.request.query_string))
        return Response(r.text, r.status_code, r.headers.items())