from flask import Response
import logging
import json
import api_headers
from CMR.Input import parse_date

class DateValidator:

    def __init__(self, request):
        self.request = request  # store the incoming request
        if 'date' in self.request.values:
            self.date = self.request.values['date']
        else:
            self.date = None

    def get_response(self):
        d = api_headers.base(mimetype='application/json')

        try:
            date = parse_date(self.date)
            resp_dict = {'date': {'original': self.date, 'parsed': date}}
            logging.debug(date)
        except ValueError as e:
            resp_dict = {'error': {'type': 'VALUE', 'report': 'Could not parse date: {0}'.format(str(e))}}

        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d)
