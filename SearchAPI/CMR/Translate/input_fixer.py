import dateparser
from datetime import datetime
import logging
import requests

from SearchAPI.asf_env import get_config
from .collections_by_platform import collections_by_platform, collections_by_platform_uat, collections_by_platform_uat_asfdev
from .datasets import platform_datasets

def input_fixer(params, is_prod: bool = False, provider: str = "ASF"):
    """
    A few inputs need to be specially handled to make the flexible input the
    legacy API allowed match what's at CMR, since we can't use wildcards on
    additional attributes
    """

    fixed_params = {}
    for k in params:
        v = params[k]
        k = k.lower()
        if k == 'lookdirection':  # Vaguely wildcard-like behavior
            if v[0].upper() not in ['L', 'R']:
                raise ValueError(f'Invalid look direction: {v}')
            fixed_params[k] = v[0].upper()
        elif k == 'flightdirection':  # Vaguely wildcard-like behavior
            if v[0].upper() not in ['A', 'D']:
                raise ValueError(f'Invalid flight direction: {v}')
            fixed_params[k] = {
                'A': 'ASCENDING',
                'D': 'DESCENDING'
            }[v[0].upper()]
        elif k == 'season':  # clamp range or abort
            if len(v) != 2:
                raise ValueError(
                    f'Invalid season, must provide two values: {v}'
                )
            if not (1 <= v[0] <= 366) or not (1 <= v[1] < 366):
                raise ValueError(
                    f'Invalid season value, must be between 1 and 366: {v}'
                )
            fixed_params[k] = v
        elif k == 'platform':
            # Legacy API allowed a few synonyms. If they're using one,
            # translate it. Also handle airsar/seasat/uavsar platform
            # conversion

            plat_aliases = {
                'S1': ['SENTINEL-1A', 'SENTINEL-1B'],
                'SENTINEL-1': ['SENTINEL-1A', 'SENTINEL-1B'],
                'SENTINEL': ['SENTINEL-1A', 'SENTINEL-1B'],
                'ERS': ['ERS-1', 'ERS-2'],
                'SIR-C': ['STS-59', 'STS-68']
            }

            plat_names = {
                'R1': 'RADARSAT-1',
                'E1': 'ERS-1',
                'E2': 'ERS-2',
                'J1': 'JERS-1',
                'A3': 'ALOS',
                'AS': 'DC-8',
                'AIRSAR': 'DC-8',
                'SS': 'SEASAT 1',
                'SEASAT': 'SEASAT 1',
                'SA': 'SENTINEL-1A',
                'SB': 'SENTINEL-1B',
                'SP': 'SMAP',
                'UA': 'G-III',
                'UAVSAR': 'G-III'
            }

            platform_list = []
            collection_list = []
            
            # If CMR adds supports for excluding results by their collection id, this would let us hide RAW data from results
            # exclude_concept_ids = ['C1214470532-ASF', 'C1214470561-ASF', 'C1327985650-ASF', 'C1327985647-ASF']
            # fixed_params['collections'] = exclude_concept_ids
            
            any_processing_level = 'processinglevel' not in params 
                       
            if any_processing_level:
                if is_prod:
                    to_collections = collections_by_platform
                elif provider == 'ASF':
                    to_collections = collections_by_platform_uat
                else:
                    to_collections = collections_by_platform_uat_asfdev
            
            for p in v:
                if p.upper() in plat_aliases:
                    for x in plat_aliases[p.upper()]:
                        if x in ['SENTINEL-1A', 'SENTINEL-1B'] and any_processing_level:
                            collection_list.extend([id_by_platform['concept-id'] for id_by_platform in to_collections[x]])
                        platform_list.append(x)
                else:
                    if ((p.upper() in plat_names and p.upper() in ['SA', 'SB']) or p.upper() in ['SENTINEL-1A', 'SENTINEL-1B'])  and any_processing_level:
                        if p.upper() in plat_names and p.upper() in ['SA', 'SB']:
                            collection_list.extend([id_by_platform['concept-id'] for id_by_platform in to_collections[plat_names[p.upper()]]])
                        else:
                            collection_list.extend([id_by_platform['concept-id'] for id_by_platform in to_collections[p.upper()]])                
                    platform_list.append(p)
            
            fixed_params[k] = list(set([
                plat_names[a.upper()] if a.upper() in plat_names else a
                for a in platform_list
            ]))
            
            if any_processing_level:
                fixed_params['collections'] = collection_list

        elif k == 'datasets':
            fixed_params['collections'] = []
            for dataset in params[k]:
                logging.warn(dataset)
                logging.warn(platform_datasets.get(dataset))
                fixed_params['collections'].extend(platform_datasets.get(dataset))
            logging.warn(fixed_params)
        elif k == 'beammode':
            beammap = {
                'STD': 'Standard'
            }
            fixed_params[k] = [
                beammap[a.upper()] if a.upper() in beammap else a for a in v
            ]
        elif k == 'beamswath':
            beammap = {
                'STANDARD': 'STD'
            }
            fixed_params[k] = [
                beammap[a.upper()] if a.upper() in beammap else a for a in v
            ]
        elif k == 'polygon':  # Do what we can to fix polygons up
            fixed_params[k] = fix_polygon(v)
        elif k == 'intersectswith':  # Need to take the parsed value here and send it to one of polygon=, line=, point=
            (t, p) = v.split(':')
            if t == 'polygon':
                p = fix_polygon(p)
            fixed_params[t] = p
        elif k == 'collectionname':
            fixed_params[k] = v.replace(',', "\\,")
        else:
            fixed_params[k] = v

    if 'start' in fixed_params or 'end' in fixed_params or 'season' in fixed_params:
        # set default start and end dates if needed, and then make sure they're formatted correctly
        # whether using the default or not
        start_s = fixed_params['start'] if 'start' in fixed_params else '1978-01-01T00:00:00Z'
        end_s = fixed_params['end'] if 'end' in fixed_params else datetime.utcnow().isoformat()

        start = dateparser.parse(start_s, settings={'RETURN_AS_TIMEZONE_AWARE': True})
        end = dateparser.parse(end_s, settings={'RETURN_AS_TIMEZONE_AWARE': True})

        # Check/fix the order of start/end
        if start > end:
            start, end = end, start

        # Final temporal string that will actually be used
        fixed_params['temporal'] = '{0},{1}'.format(
            start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            end.strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        # add the seasonal search if requested now that the regular dates are
        # sorted out
        if 'season' in fixed_params:
            fixed_params['temporal'] += ',{0}'.format(
                ','.join(str(x) for x in fixed_params['season'])
            )

        # And a little cleanup
        fixed_params.pop('start', None)
        fixed_params.pop('end', None)
        fixed_params.pop('season', None)

    return fixed_params


def fix_polygon(v):
    # Trim whitespace and split it up
    v = v.replace(' ', '').split(',')

    # If the polygon doesn't wrap, fix that
    if v[0] != v[-2] or v[1] != v[-1]:
        v.extend(v[0:2])

    # Do a quick CMR query to see if the shape is wound correctly
    logging.debug('Checking winding order')
    cfg = get_config()

    r = requests.post(
        cfg['cmr_base'] + cfg['cmr_api'],
        headers=cfg['cmr_headers'],
        data={
            'polygon': ','.join(v),
            'provider': 'ASF',
            'page_size': 1,
            'concept-id': 'C1266376001-ASF',
            'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'
        }
    )

    if r.status_code == 200:
        logging.debug('Winding order looks good')
    else:
        if 'Points must be provided in counter-clockwise order.' in r.text or 'Please check the order of your points.' in r.text:
            logging.debug('Backwards polygon, attempting to repair')
            logging.debug(r.text)
            it = iter(v)
            rev = reversed(list(zip(it, it)))
            rv = [i for sub in rev for i in sub]

            r = requests.post(
                    cfg['cmr_base'] + cfg['cmr_api'],
                    headers=cfg['cmr_headers'],
                    data={
                        'polygon': ','.join(rv),
                        'provider': 'ASF',
                        'page_size': 1,
                        'concept-id': 'C1266376001-ASF',
                        'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'
                    }
                )

            if r.status_code == 200:
                logging.debug('Polygon repaired')
                v = rv
            else:
                logging.warning(
                    'Polygon repair needed but reversing the '
                    'points did not help, query will fail'
                )
                raise ValueError(f'Invalid coordinates, could not repair: {v}')
        else:
            raise ValueError(
                f'Invalid coordinates, could not repair: {v}'
            )

    return ','.join(v)
