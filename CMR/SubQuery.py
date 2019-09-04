import requests
from math import ceil
import logging
import re
from CMR.Translate import parse_cmr_response
from CMR.Exceptions import CMRError
from Analytics import post_analytics
from asf_env import get_config
from time import time, sleep

class CMRSubQuery:

    def __init__(self, params, extra_params, analytics=True):
        self.params = params
        self.extra_params = extra_params
        self.analytics = analytics
        self.sid = None
        self.hits = 0
        self.results = []

        fixed = []
        for p in self.params:
            fixed.extend(p.items())

        self.params = fixed

        self.params.extend(self.extra_params.items())

        # Platform-specific hacks
        # We do them at the subquery level in case the main query crosses platforms
        # that don't suffer these issue.
        use_asf_frame = False
        for p in self.params:
            if p[0] == 'platform[]' and p[1] in ['SENTINEL-1A', 'SENTINEL-1B', 'ALOS']:
                use_asf_frame = True
        if use_asf_frame:
            # Sentinel/ALOS: always use asf frame instead of esa frame
            for n, p in enumerate(self.params):
                if isinstance(p[1], str):
                    m = re.search(r'CENTER_ESA_FRAME', p[1])
                    if m is not None:
                        logging.debug('Sentinel/ALOS subquery, using ASF frame instead of ESA frame')
                        self.params[n] = (p[0], p[1].replace(',CENTER_ESA_FRAME,', ',FRAME_NUMBER,'))

        logging.debug('New CMRSubQuery object with params: {0}'.format(self.params))

    def get_count(self):
        s = requests.Session()
        s.headers.update({'Client-Id': 'vertex_asf'})

        cfg = get_config()

        # over-ride scroll and page size for count queries to minimize data transfer, since we can't do a HEAD request like this anymore
        params = [x for x in self.params if x[0] not in ['scroll', 'page_size']]
        params.append(('page_size', 0))

        r = s.post(cfg['cmr_base'] + cfg['cmr_api'], data=params)
        if 'CMR-hits' not in r.headers:
            raise CMRError(r.text)
        self.hits = int(r.headers['CMR-hits'])
        logging.debug('CMR reported {0} hits'.format(self.hits))
        return int(r.headers['CMR-hits'])

    def get_results(self):
        #self.get_count()
        s = requests.Session()
        s.headers.update({'Client-Id': 'vertex_asf'})

        logging.debug('Processing page 1')
        r = self.get_page(s)
        if r is None:
            return
        self.hits = int(r.headers['CMR-hits'])
        self.sid = r.headers['CMR-Scroll-Id']
        logging.debug('CMR reported {0} hits for session {1}'.format(self.hits, self.sid))

        logging.debug('Parsing page 1')
        for p in parse_cmr_response(r):
            yield p

        pages = list(range(2, int(ceil(float(self.hits) / float(self.extra_params['page_size']))) + 1))
        logging.debug('Planning to fetch additional {0} pages'.format(len(pages)))
        s.headers.update({'CMR-Scroll-Id': self.sid})

        # fetch multiple pages of results if needed, yield a product at a time
        for page_num in pages:
            logging.debug('Processing page {0}'.format(page_num))
            page = self.get_page(s)
            logging.debug('Parsing page {0}'.format(page_num))
            for p in parse_cmr_response(page):
                yield p
            logging.debug('Parsing page {0} complete'.format(page_num))
            logging.debug('Processing page {0} complete'.format(page_num))

        logging.debug('Done fetching results: got {0}/{1}'.format(len(self.results), self.hits))
        return

    def get_page(self, s):
        logging.debug('Page fetch starting')
        cfg = get_config()
        max_retry = 3
        for attempt in range(max_retry): # Sometimes CMR is on the fritz, retry for a bit
            r = s.post(cfg['cmr_base'] + cfg['cmr_api'], data=self.params)
            if self.analytics:
                post_analytics(pageview=False, events=[{'ec': 'CMR API Status', 'ea': r.status_code}])
            if r.status_code != 200:
                logging.error('Bad news bears! CMR said {0} on session {1}'.format(r.status_code, self.sid))
                logging.error('Attempt {0} of {1}'.format(attempt + 1, max_retry))
                logging.error('Params sent to CMR:')
                logging.error(self.params)
                logging.error('Headers sent to CMR:')
                logging.error(s.headers)
                logging.error('Error body: {0}'.format(r.text))
                sleep(0.5) # Yikes, but maybe give CMR a chance to sort itself out
            else:
                logging.debug('Page fetch complete')
                return r
        # CMR isn't cooperating, just move on?
        logging.error('Max number of retries reached, moving on')
        return
