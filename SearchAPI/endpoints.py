from flask import Response
import json
import SearchAPI.api_headers as api_headers
import logging

from WKTUtils import FilesToWKT, RepairWKT
import SearchAPI.MissionList as MissionList
from SearchAPI.CMR.Input import parse_date


########################################################
class FilesToWKT_Endpoint:
    def __init__(self, request):
        # Find out if the user passed us files:
        self.files = []
        if 'files' in request.files and len(list(request.files.getlist('files'))) > 0:
            for file in list(request.files.getlist('files')):
                self.files.append(file)


    def get_response(self):
        resp_dict = self.make_response()
        ###### For backwards compatibility #################################
        if "parsed wkt" in resp_dict:                                      #
            repaired_json = RepairWKT.repairWKT(resp_dict["parsed wkt"])   #
            for key, val in repaired_json.items():                         #
                resp_dict[key] = val                                       #
        ####################################################################
        d = api_headers.base(mimetype='application/json')
        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d, mimetype='application/json')

    def make_response(self):
        if self.files == []:
            return {'errors': [{'type': 'POST', 'report': "Could not find 'files' in post request."}]}
        return FilesToWKT.filesToWKT(self.files).getWKT()


########################################################
class RepairWKT_Endpoint:
    def __init__(self, request):
        if 'wkt' in request.local_values:
            self.wkt = request.local_values["wkt"].upper()
        else:
            self.wkt = None

    def get_response(self):
        resp_dict = self.make_response()
        d = api_headers.base(mimetype='application/json')
        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d, mimetype='application/json')

    def make_response(self):
        if self.wkt == None:
            return {'errors': [{'type': 'POST', 'report': "Could not find 'wkt' in post request."}] }
        else:
            return RepairWKT.repairWKT(self.wkt)


########################################################
class DateValidator_Endpoint:
    def __init__(self, request):
        if 'date' in request.local_values:
            self.date = request.local_values['date']
        else:
            self.date = None

    def get_response(self):
        resp_dict = self.make_response()
        d = api_headers.base(mimetype='application/json')
        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d, mimetype='application/json')

    def make_response(self):
        if self.date == None:
            return {'errors': [{'type': 'POST', 'report': "Could not find 'date' in post request."}]}
        try:
            date = parse_date(self.date)
            logging.debug(date)
        except ValueError as e:
            return {'errors': [{'type': 'VALUE', 'report': f'Could not parse date: {e}'}]}
        return {'date': {'original': self.date, 'parsed': date}}


########################################################
class MissionList_Endpoint:
    def __init__(self, request):
        if 'platform' in request.local_values:
            self.platform = request.local_values['platform'].upper()
        else:
            self.platform = None

    def get_response(self):
        resp_dict = self.make_response()
        d = api_headers.base(mimetype='application/json')
        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d, mimetype='application/json')

    def make_response(self):
        # Setup data for request.
        data = {
            'include_facets': 'true',
            'provider': 'ASF'
        }
        # If you set a platform:
        if self.platform != None:
            if self.platform == 'UAVSAR':
                data['platform[]'] = 'G-III'
                data['instrument[]'] = 'UAVSAR'
            elif self.platform == 'AIRSAR':
                data['platform[]'] = 'DC-8'
                data['instrument[]'] = 'AIRSAR'
            elif self.platform == 'SENTINEL-1 INTERFEROGRAM (BETA)':
                data['platform[]'] = 'SENTINEL-1A'
            else:
                data['platform[]'] = self.platform
        return MissionList.getMissions(data)
