import logging
from asf_env import get_config
import api_headers
import requests
from flask import Response
import json
from lxml import etree as ET

class MissionList:

    def __init__(self, request):
        self.request = request  # store the incoming request
        if 'platform' in self.request.values:
            self.platform = self.request.values['platform'].upper()
        else:
            self.platform = None

        data = {
            'include_facets': 'true',
            'provider': 'ASF'
        }
        if self.platform == 'UAVSAR':
            data['platform[]'] = 'G-III'
            data['instrument[]'] = 'UAVSAR'
        elif self.platform == 'AIRSAR':
            data['platform[]'] = 'DC-8'
            data['instrument[]'] = 'AIRSAR'
        elif self.platform == 'SENTINEL-1 INTERFEROGRAM (BETA)':
            data['platform[]'] = 'SENTINEL-1A'
        elif self.platform is not None:
            data['platform[]'] = self.platform
        self.data = data

    def getMissions(self):
        cfg = get_config()

        r = requests.post(cfg['cmr_base'] + cfg['cmr_collections'], headers=cfg['cmr_headers'], data=self.data)
        if r.status_code != 200:
            return { 'error': {'type': 'CMR_ERROR', 'report': 'CMR Error: {0}'.format(r.text)}}

        try:
            root = ET.fromstring(r.text.encode('latin-1'))
        except ET.ParseError as e:
            return {'error': {'type': 'CMR_ERROR', 'report': 'Error parsing XML from CMR: {0}'.format(e)}}

        missions = [f.text for f in root.findall('.//facets/facet[@field="project"]/value')]
        missions = sorted(missions, key=lambda s: s.casefold())
        logging.debug(missions)

        # All done
        return {
            'result': missions
        }

    def get_response(self):
        d = api_headers.base(mimetype='application/json')

        resp_dict = self.make_response()

        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d)

    def make_response(self):
        return self.getMissions()
