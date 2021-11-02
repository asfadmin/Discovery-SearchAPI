import logging
from math import ceil
import re
from time import sleep, perf_counter

import requests
from flask import request

from asf_env import get_config
from CMR.Translate import parse_cmr_response
from CMR.Exceptions import CMRError


class CMRSubQuery:
    def __init__(self, req_fields, params, extra_params):
        self.params = params
        self.extra_params = extra_params
        self.req_fields = req_fields
        self.sid = None
        self.hits = 0
        self.results = []

        self.scroll = get_config()['cmr_scroll']

        self.params = self.combine_params(self.params, self.extra_params)

        self.headers = {}
        
        token = request.args.get("cmr_token")
        if token != None:
            self.headers['Authorization'] = f'Bearer {token}'

        if self.should_use_asf_frame():
            self.use_asf_frame()

        logging.debug(f'New CMRSubQuery object with params: {self.params}')

    def get_page_size(self):
        for param in self.params:
            if 'page_size' in param:
                return param[1]

    def combine_params(self, params, extra_params):
        fixed = []
        for p in params + extra_params:
            fixed.extend(p.items())

        final = []
        for p in fixed:
            if p[0] in ['readable_granule_name[]', 'granule_ur[]']:
                for g in p[1].split(','):
                    final.append((p[0], g))
            else:
                final.append(p)
        return final

    def should_use_asf_frame(self):
        asf_frame_platforms = ['SENTINEL-1A', 'SENTINEL-1B', 'ALOS']

        return any([
            p[0] == 'platform[]' and p[1] in asf_frame_platforms
            for p in self.params
        ])

    def use_asf_frame(self):
        """
        Sentinel/ALOS: always use asf frame instead of esa frame

        Platform-specific hack
        We do them at the subquery level in case the main query crosses
        platforms that don't suffer these issue.
        """

        for n, p in enumerate(self.params):
            if not isinstance(p[1], str):
                continue

            m = re.search(r'CENTER_ESA_FRAME', p[1])
            if m is None:
                continue

            logging.debug(
                'Sentinel/ALOS subquery, using ASF frame instead of ESA frame'
            )

            self.params[n] = (
                p[0],
                p[1].replace(',CENTER_ESA_FRAME,', ',FRAME_NUMBER,')
            )

    def get_count(self):
        # over-ride scroll and page size for count queries to minimize data
        # transfer, since we can't do a HEAD request like this anymore
        params = [
            param for param in self.params
            if param[0] not in ['scroll', 'page_size']
        ]
        params.append(('page_size', 0))

        session = self.asf_session()
        url = self.cmr_api_url()

        cmr_request = session.post(url, data=params, headers=self.headers)

        if 'CMR-hits' not in cmr_request.headers:
            raise CMRError(cmr_request.text)

        self.hits = int(cmr_request.headers['CMR-hits'])

        logging.debug(f'CMR reported {self.hits} hits')

        return int(cmr_request.headers['CMR-hits'])

    def get_results(self):
        logging.debug('Processing page 1')

        session = self.asf_session()
        response = self.get_page(session, 1)

        if response is None:
            return

        self.hits = int(response.headers['CMR-hits'])
        self.sid = None
        if self.scroll:
            self.sid = response.headers['CMR-Scroll-Id']
            request.cmr_scroll_sessions.append(self.sid)

        logging.debug(f'CMR reported {self.hits} hits for session {self.sid}')
        logging.debug('Parsing page 1')

        for p in parse_cmr_response(response, self.req_fields):
            yield p

        hits = float(self.hits)
        page_size = float(self.get_page_size())
        num_pages = int(ceil(hits / page_size)) + 1

        logging.debug(f'Planning to fetch additional {num_pages} pages')
        if self.scroll:
            session.headers.update({'CMR-Scroll-Id': self.sid})

        # fetch multiple pages of results if needed, yield a product at a time
        for page_num in range(2, num_pages):
            logging.debug(f'Processing page {page_num}')

            page = self.get_page(session, page_num)

            logging.debug(f'Parsing page {page_num}')

            for parsed_page in parse_cmr_response(page, self.req_fields):
                yield parsed_page

            logging.debug(f'Parsing page {page_num} complete')
            logging.debug(f'Processing page {page_num} complete')

        logging.debug(f'Done fetching results: got {len(self.results)}/{self.hits}')

        return

    def get_page(self, session, page_num):
        logging.debug('Page fetch starting' + (' (scrolled)' if self.scroll else ' (paged)'))
        max_retry = 3

        # Sometimes CMR is on the fritz, retry for a bit
        for attempt in range(max_retry):
            q_start = perf_counter()

            api_url = self.cmr_api_url()
            if self.scroll == False:
                response = session.post(api_url, data=self.params + [('page_num', page_num)], headers=self.headers)
            else:
                response = session.post(api_url, data=self.params, headers=self.headers)

            query_duration = perf_counter() - q_start
            logging.debug(f'CMR query time: {query_duration}')

            if query_duration > 10:
                self.log_slow_cmr_response(session, response, query_duration)

            if response.status_code != 200:
                self.log_bad_cmr_response(
                    attempt, max_retry, response, session
                )
                if response.status_code == 404:
                    logging.error('Halting without retries due to 404')
                    break

                # CMR a chance to sort itself out
                sleep(0.5)
                continue

            logging.debug('Page fetch complete')
            return response

        logging.error('Max number of retries reached, moving on')
        return

    def asf_session(self):
        session = requests.Session()
        headers = get_config()['cmr_headers']
        session.headers.update(headers)
        logging.debug('New requests.Session with headers:')
        logging.debug(session.headers)

        return session

    def cmr_api_url(self):
        cfg = get_config()

        base, path = cfg['cmr_base'], cfg['cmr_api']
        url = f'{base}{path}'

        return url

    def log_slow_cmr_response(self, session, response, response_time):
        logging.error(f'Slow CMR response: {response_time} seconds')
        logging.error('Params sent to CMR:')
        logging.error(self.params)
        logging.error('Headers sent to CMR:')
        logging.error(session.headers)
        logging.error(f'Response code: {response.status_code}')

    def log_bad_cmr_response(self, attempt, max_retry, response, session):
        logging.error(
            f'Bad news bears! CMR said {response.status_code}' +
            (f' on session {self.sid}' if self.scroll else '')
        )
        logging.error(f'Attempt {attempt + 1} of {max_retry}')
        logging.error('Params sent to CMR:')
        logging.error(self.params)
        logging.error('Headers sent to CMR:')
        logging.error(session.headers)
        logging.error(f'Error body: {response.text}')
