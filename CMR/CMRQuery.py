import urls
import requests
from flask import Response, make_response
from CMR.CMRTranslate import translators

class CMRQuery:
    
    def __init__(self, params=None, max_results=None, output='metalink'):
        self.echo10_results = []
        self.params = params
        self.max_results = max_results
        self.output = output
    
    def get_results(self):
        r = requests.post(urls.cmr_api, data=self.params)
        
        # forward anything other than a 200
        if r.status_code != 200:
            return Response(r.text, r.status_code, r.header_items())
        
        hits = int(r.headers['CMR-hits'])
        
        return make_response(translators.get(self.output, translators['metalink'])(r))
        
        # some probably defunct paging support but I want to keep it handy for later
        '''
        if output == 'echo10':
            results = r.text
        else:
            results = parse_cmr_xml(r.text)
        if hits > params['page_size']:
            for n in range(hits // params['page_size'] - 1): # parallelize this!!
                if n * params['page_size'] >= max_results:
                    break
                if output == 'echo10':
                    results += r.text
                else:
                    results.extend(parse_cmr_xml(requests.post(urls.cmr_api, data=params, headers={'CMR-Scroll-Id': session_id}).text))
                logging.debug('scrolled results downloaded for session {0}: {1}/{2}'.format(session_id, len(results), max_results))
        if output != 'echo10': # don't bother trimming if the output is echo10, it's close enough
            logging.debug('pulled {0} results for session {1}, trimming'.format(len(results), session_id))
            results = results[0:max_results] # trim off any excess from the last page
        text = translators.get(output, translators['metalink'])(results)
        return make_response(text)'''