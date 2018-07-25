import requests
from math import ceil
import logging
import re
from CMR.Translate import parse_cmr_response
from CMR.Exceptions import CMRError
from Analytics import post_analytics
from asf_env import get_config

class CMRSubQuery:
    
    def __init__(self, params, extra_params, max_results=1000000, count=False):
        self.params = params
        self.extra_params = extra_params
        self.max_results = max_results if max_results is not None else 1000000
        self.sid = None
        self.hits = 0
        self.results = []
        self.count = count
        
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
            
            # ALOS: translate beamswath values to beammode/offnadirangle
            if plat.upper() in ['ALOS']:
                for n, p in enumerate(self.params):
                    if isinstance(p[1], str):
                        m = re.search(r'BEAM_MODE_TYPE', p[1])
                        if m is not None:
                            logging.debug('ALOS subquery, converting beamswath to beammode/offnadirangle')
                            logging.debug('n: {0}, p: {1}'.format(n, p))
        
        logging.debug('new CMRSubQuery object ready to go')
    
    def get_results(self):
        s = requests.Session()
        s.headers.update({'Client-Id': 'vertex_asf'})
        
        # Get the first page of results
        r = self.get_page(0, s)
        
        #post_analytics(pageview=False, events=[{'ec': 'CMR API Status', 'ea': r.status_code}])
        # forward anything other than a 200
        if r.status_code != 200:
            raise CMRError(r.text)
        
        if self.count:
            return int(r.headers['CMR-hits'])
            
        if self.max_results > self.hits:
            self.max_results = self.hits
        
        self.results = parse_cmr_response(r)
        
        # enumerate additional pages out to hit count or max_results, whichever is fewer (excluding first page)
        pages = list(range(1, int(min(ceil(float(self.hits) / float(self.extra_params['page_size'])), ceil(float(self.max_results) / float(self.extra_params['page_size']))))))
        logging.debug('Preparing to fetch {0} additional pages'.format(len(pages)))
        
        # fetch multiple pages of results if needed
        for p in pages:
            self.results.extend(parse_cmr_response(self.get_page(p, s)))
        logging.debug('Done fetching results: got {0}/{1}'.format(len(self.results), self.hits))
        
        # trim the results if needed
        if self.max_results is not None and len(self.results) > self.max_results:
            logging.debug('Trimming subquery results from {0} to {1}'.format(len(self.results), self.max_results))
            self.results = self.results[0:self.max_results]
        
        return self.results
    
    def get_page(self, p, s):
        logging.debug('Fetching page {0}'.format(p+1))
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
        post_analytics(pageview=False, events=[{'ec': 'CMR API Status', 'ea': r.status_code}])
        if r.status_code != 200:
            logging.error('Bad news bears! CMR said {0} on session {1}'.format(r.status_code, self.sid))
        else:
            logging.debug('Fetched page {0}'.format(p + 1))
        return r