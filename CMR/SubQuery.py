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
        self.current_page = 0
        self.last_page_time = time()

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

        logging.debug('new CMRSubQuery object ready to go')

    def get_count(self):
        s = requests.Session()
        s.headers.update({'Client-Id': 'vertex_asf'})
        r = s.head(get_config()['cmr_api'], data=self.params)
        if 'CMR-hits' not in r.headers:
            raise CMRError(r.text)
        return int(r.headers['CMR-hits'])

    def get_results(self):
        s = requests.Session()
        s.headers.update({'Client-Id': 'vertex_asf'})

        # Get the first page of results
        r = self.get_page(s)

        #post_analytics(pageview=False, events=[{'ec': 'CMR API Status', 'ea': r.status_code}]) if self.analytics else None
        # forward anything other than a 200
        if r.status_code != 200:
            raise CMRError(r.text)

        for p in parse_cmr_response(r):
            yield p

        # enumerate additional pages out to hit count
        # FIXME: this is ugly and we shouldn't even need to enumerate pages anymore
        # since we're scrolling, we should just run until no results come back
        pages = list(range(1, int(ceil(float(self.hits) / float(self.extra_params['page_size'])))))
        logging.debug('Preparing to fetch {0} additional pages'.format(len(pages)))

        # fetch multiple pages of results if needed, yield a product at a time
        for page in pages:
            for p in parse_cmr_response(self.get_page(s)):
                yield p

        logging.debug('Done fetching results: got {0}/{1}'.format(len(self.results), self.hits))
        return

    def get_page(self, s):
        logging.debug('Fetching page {0}'.format(self.current_page + 1))
        if self.sid is None:
            r = s.post(get_config()['cmr_api'], data=self.params)
            if 'CMR-hits' not in r.headers:
                raise CMRError(r.text)
            self.hits = int(r.headers['CMR-hits'])
            self.sid = r.headers['CMR-Scroll-Id']
            s.headers.update({'CMR-Scroll-Id': self.sid})
            logging.debug('CMR reported {0} hits for session {1}'.format(self.hits, self.sid))
        else:
            r = s.post(get_config()['cmr_api'], data=self.params)
        post_analytics(pageview=False, events=[{'ec': 'CMR API Status', 'ea': r.status_code}]) if self.analytics else None
        if r.status_code != 200:
            logging.error('Bad news bears! CMR said {0} on session {1}'.format(r.status_code, self.sid))
            logging.error('Currently on page {0}'.format(self.current_page + 1))
            if(self.current_page < 1):
                logging.error('This was the first page! Subquery initialized {0} seconds ago'.format(time() - self.last_page_time))
            else:
                logging.error('Last page fetched {0} seconds ago'.format(time() - self.last_page_time))
            logging.error('Params that caused this error:')
            logging.error(self.params)
            logging.error('Error body: {0}'.format(r.text))
        else:
            logging.debug('Fetched page {0}'.format(self.current_page + 1))
        self.last_page_time = time()
        self.current_page += 1
        return r
