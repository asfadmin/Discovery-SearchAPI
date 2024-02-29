from flask import request
from .input_map import input_map

from SearchAPI.CMR.Output import output_translators
import json
import requests
from SearchAPI.asf_env import get_config

from shapely import wkt
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
def translate_params(p):
    """
    Translate supported params into CMR params
    """
    params = {}

    for key in p:
        val = p[key]
        key = key.lower()
        if key not in input_map():
            raise ValueError(f'Unsupported parameter: {key}')
        if key == 'intersectswith': # Gotta catch this suuuuper early
            s = requests.Session()
            repair_params = dict({'wkt': val})
            try:
                repair_params['maturity'] = request.temp_maturity
            except AttributeError:
                pass
            response = json.loads(s.post(get_config()['this_api'] + '/services/utils/wkt', data=repair_params).text)
            if 'errors' in response:
                raise ValueError(f'Could not repair WKT: {val}')
            val = response['wkt']['wrapped']
            shape = wkt.loads(response['wkt']['unwrapped'])
            if _should_use_bbox(shape):
                bbox = _get_bbox(shape)
                try:
                    params['bbox'] = input_map()['bbox'][2](bbox)
                    continue
                except ValueError as exc:
                    raise ValueError(f'{key}: {exc}') from exc
        try:
            params[key] = input_map()[key][2](val)
        except ValueError as exc:
            raise ValueError(f'{key}: {exc}') from exc

    # be nice to make this not a special case
    output = 'metalink'

    if 'output' in params and params['output'].lower() in output_translators():
        output = params['output'].lower()

    if 'output' in params:
        del params['output']
    max_results = None

    if 'maxresults' in params:
        max_results = params['maxresults']
        if max_results < 1:
            raise ValueError(
                f'Invalid maxResults, must be > 0: {max_results}'
            )
        del params['maxresults']

    return params, output, max_results

def _get_bbox(aoi: BaseGeometry):
    # If a wide rectangle is provided, make sure to use the bounding box
    # instead of the wkt for better responses from CMR
    # This will provide better results with AOI's near poles
    bounds = aoi.boundary.bounds
    if bounds[0] > 180 or bounds[2] > 180:
        bounds = [(x + 180) % 360 - 180 if idx % 2 == 0 and abs(x) > 180 else x for idx, x in enumerate(bounds)]

    bottom_left = [str(coord) for coord in bounds[:2]]
    top_right = [str(coord) for coord in bounds[2:]]

    bbox = ','.join([*bottom_left, *top_right])
    return  bbox


def _should_use_bbox(shape: BaseGeometry):
    """
    If the passed shape is a polygon, and if that polygon
    is equivalent to it's bounding box (if it's a rectangle),
    we should use the bounding box to search instead
    """
    if isinstance(shape, Polygon):
        coords = [
            [shape.bounds[0], shape.bounds[1]], 
            [shape.bounds[2], shape.bounds[1]],
            [shape.bounds[2], shape.bounds[3]],
            [shape.bounds[0], shape.bounds[3]],
        ]
        return shape.equals(Polygon(shell=coords))
    
    return False