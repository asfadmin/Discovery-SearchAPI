import requests
from flask import Response
import api_headers

# Note to self: Make sure you run 'pip install git+ssh://git@github.com/asfadmin/Discovery-UtilsAPI.git' first!
from UtilsAPI import FilesToWKT, repairWKT

class FilesToWKT_Endpoint:
	def __init__(self, request):
        # Find out if the user passed us files:
        if 'files' in request.files and len(list(request.files.getlist('files'))) > 0:
            self.files = request.files.getlist("files")
        else:
            self.files = None

    def get_response(self):
    	if self.files == None:
    		return {'errors': [{'type': 'POST', 'report': "Could not find 'files' in post request."}]}

    	d = api_headers.base(mimetype='application/json')
        resp_dict = self.make_response()
        ###### For backwards compatibility ######################
        if "parsed wkt" in resp_dict:                           #
            repaired_json = repairWKT(resp_dict["parsed wkt"])  #
            for key, val in repaired_json.items():              #
                resp_dict[key] = val                            #
        #########################################################
        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d)

    def make_response(self):
    	return FilesToWKT(self.files)
