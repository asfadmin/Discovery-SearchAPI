import requests
from math import ceil
import logging
import re
from CMR.Translate import parse_cmr_response
from CMR.Exceptions import CMRError
from Analytics import post_analytics
from asf_env import get_config
from time import time

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
        plat = None
        for p in self.params:
            if isinstance(p[1], str):
                m = re.search(r'ASF_PLATFORM,(.+)', p[1])
                if m is not None:
                    plat = m.group(1)
                    break
        if plat is not None:
            # Sentinel/ALOS: always use asf frame instead of esa frame
            if plat.upper() in ['ALOS', 'SENTINEL-1A', 'SENTINEL-1B']:
                for n, p in enumerate(self.params):
                    if isinstance(p[1], str):
                        m = re.search(r'CENTER_ESA_FRAME', p[1])
                        if m is not None:
                            logging.debug('Sentinel/ALOS subquery, using ESA frame instead of ASF frame')
                            self.params[n] = (p[0], p[1].replace(',CENTER_ESA_FRAME,', ',FRAME_NUMBER,'))

        logging.debug('New CMRSubQuery object with params: {0}'.format(self.params))

    def get_count(self):
        s = requests.Session()
        s.headers.update({'Client-Id': 'vertex_asf'})
        r = s.head(get_config()['cmr_api'], data=self.params)
        if 'CMR-hits' not in r.headers:
            raise CMRError(r.text)
        self.sid = r.headers['CMR-Scroll-Id']
        self.hits = int(r.headers['CMR-hits'])
        logging.debug('CMR reported {0} hits for session {1}'.format(self.hits, self.sid))
        return int(r.headers['CMR-hits'])

    def get_results(self):
        #self.get_count()
        s = requests.Session()
        s.headers.update({'Client-Id': 'vertex_asf'})

        logging.debug('Processing page 1')
        r = self.get_page(s)

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
        r = s.post(cfg['cmr_api'], data=self.params)
        if self.analytics:
            post_analytics(pageview=False, events=[{'ec': 'CMR API Status', 'ea': r.status_code}])
        if r.status_code != 200:
            logging.error('Bad news bears! CMR said {0} on session {1}'.format(r.status_code, self.sid))
            logging.error('Params that caused this error:')
            logging.error(self.params)
            logging.error('Error body: {0}'.format(r.text))
        else:
            logging.debug('Page fetch complete')
        return r
