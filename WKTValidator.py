from flask import Response
import json
import api_headers
from APIUtils import repairWKT

class WKTValidator:

    def __init__(self, request):
        self.request = request  # store the incoming request
        
        if 'wkt' in self.request.values:
            self.wkt = self.request.values["wkt"].upper()
        else:
            self.wkt = None

    def get_response(self):
        d = api_headers.base(mimetype='application/json')
        resp_dict = self.make_response()
        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d)

    def make_response(self):
        if self.wkt == None:
            return {'error': {'type': 'POST', 'report': "Could not find 'wkt' in post request."} }
        else:
            return repairWKT(self.wkt)
