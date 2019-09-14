import logging
from CMR.Input import parse_wkt
from geomet import wkt
from asf_env import get_config
import requests
import shapely.wkt
import shapely.ops
from shapely.geometry import Polygon, MultiPolygon
import re



class simplifyWKT_v2():
    def __init__(self, wkt_str):
        self.shapes = []
        self.error = None
        self.repairs = []
        try:
            wkt_json = wkt.loads(wkt_str)
        except ValueError as e:
            self.error = { 'error': {'type': 'VALUE', 'report': 'Could not parse WKT: {0}'.format(str(e))} }
            return
        except TypeError as e:
            self.error =  { 'error': {'type': 'TYPE', 'report': str(e)} }
            return

        # Turn the json into a list of individual shapes:
        # (Populates self.shapes)
        self.__updateShapes(wkt_json)


        # See if a merge is required or not:
        if len(self.shapes) == 0:
            self.error = { 'error': {'type': 'VALUE', 'report': 'Could not parse WKT: No valid shapes found'} }
            return
        elif len(self.shapes) == 1:
            self.wkt_unwrapped = shapely.wkt.dumps(self.shapes[0])
        else:
            shapely_union = self.__mergeShapelyList(self.shapes)
            self.wkt_unwrapped = shapely.wkt.dumps(shapely_union)

        self.wkt_wrapped = self.wkt_unwrapped
        ###########
        # TODO: Add wrapped vs unwrapped:
        ###########
        # Fixes to apply AFTER it's one shape:
        #   clamp/wrap each coords. shapely is okay with (9000 9000) so not a problem
        #       also makes storing wrapped vs unwrapped easy
        #   Reverse winding order if neededself.wkt_unwrappedself.wkt_unwrapped
        #   Reduce number of points



    def get_simplified_json(self):
        if self.error != None:
            return self.error
        else:
            return { 
                'wkt': {
                    'wrapped': self.wkt_wrapped,
                    'unwrapped': self.wkt_unwrapped
                },
                'repairs': self.repairs
            }


    # Update self.shapes with shapely objects based on the original wkt_json:
    def __updateShapes(self, wkt_json):
        # If GEOMETRY COLLECTION, grab the shapes inside it:
        if wkt_json['type'].upper() == 'GEOMETRYCOLLECTION':
            inner_wkt = wkt_json["geometries"]
            for shape in inner_wkt:
                # Run each shape through again. Could be another geo collection:
                self.__updateShapes(shape)

        # Else if one of the "MULTI" shapes, send each sub-shape through again:
        # (MULTISTRING, MULTIPOLYGON, MULTIPOINT, MULTILINESTRING, etc...)
        elif wkt_json['type'].upper()[0:5] == 'MULTI':
            for i in range(len(wkt_json["coordinates"])):
                sub_shape = {'type': wkt_json['type'][5:], 'coordinates':  wkt_json["coordinates"][i]  }
                self.__updateShapes(sub_shape)

        # If supported shape, just add it:
        elif wkt_json['type'].upper() in ['POINT', 'LINESTRING', 'POLYGON']:
            # Quick check to see if the polygon forms a closed loop:
            if wkt_json['type'].upper() == 'POLYGON':
                # Only grab the first set of coords. (Take out any holes):
                coords = wkt_json['coordinates'][0]
                # If the first set does not equal the last set:
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                    self.repairs.append({
                        'type': 'CLOSE',
                        'report': 'Closed open polygon'
                    })
                    logging.debug(self.repairs[-1])
                # Save the coords, connected and w/out holes, back to the shape
                wkt_json['coordinates'] = [coords]
            basic_shape = shapely.wkt.loads(wkt.dumps(wkt_json))
            self.shapes.append(basic_shape)

        else: 
            wkt_json, successful = self.__convexHullShape(wkt_json)
            # If it was able to create a shape from the points:
            if successful:
                self.repairs.append({
                    'type': 'CONVEX_HULL',
                    'report': 'Shape {} was not of a supported type; using it\'s convex hull instead'.format(wkt_json['type'])
                })
                logging.debug(self.repairs[-1])
                basic_shape = shapely.wkt.loads(wkt.dumps(wkt_json))
                self.shapes.append(basic_shape)
            else:
                self.repairs.append({
                    'type': 'CONVEX_HULL_FAILED',
                    'report': 'Could not parse points inside unknown shape: {}. Skipping it.'.format(wkt_json['type'])
                })
                logging.debug(self.repairs[-1])


    # Takes a geomet.wkt object, and returns the convex_hull of that shape
    def __convexHullShape(self, wkt_json):
            match_coords = match_coords = r'(\[\s*-?((\d+\.\d*)|(\d*\.\d+)|(\d+))\s*,\s*-?((\d+\.\d*)|(\d*\.\d+)|(\d+))\s*\])'
            coords = re.findall(match_coords,str(wkt_json["coordinates"]))
            # If you couldn't find any points:
            if len(coords) == 0:
                return None, False

            all_coords = []
            for i in range(len(coords)):
                # Group 0 = "[ 1.0, 1.0 ]" as a literall string. Convert to list of floats:
                this_set = coords[i][0].strip('][').split(', ')
                all_coords.append([ float(this_set[0]), float(this_set[1]) ])
            # Convex_hull and add the new shape:
            MultiPoint = {'type': 'MultiPoint', 'coordinates': all_coords }
            # Quicky convert to shapely obj for the convex hull, then back again:
            shape = shapely.wkt.loads(wkt.dumps(MultiPoint))
            return wkt.loads(shapely.wkt.dumps(shape.convex_hull))
            
    ########
    # TODO:
    # Return None if merge failed, or the single shape itself?
    # Lets me call this function, then if none, convex hall
    # each single shape, then if None again, just convex_hull everything.
    ########
    def __mergeShapelyList(self, shapely_list):
        # Merge the shape, then apply some repairs:
        union = shapely.ops.unary_union(shapely_list)

        if union.geom_type.upper() in ['GEOMETRYCOLLECTION', 'MULTIPOLYGON']:
            # This means there are shapes by themselves. Convex_hull everything:
            union = wkt.loads(shapely.wkt.dumps(union))
            union = self.__convexHullShape(union)
            return shapely.wkt.loads(wkt.dumps(union))

        elif union.geom_type.upper() == 'POLYGON':
            # This removes any holes inside the poly:
            return Polygon(union.exterior.coords)
        elif union.geom_type.upper() == 'MULTILINESTRING':
            line_merge = shapely.ops.linemerge(union)
            # If it collapsed into one line:
            if line_merge.geom_type.upper() == 'LINESTRING':
                return True, line_merge
            else:
                return False, line_merge
        elif union.geom_type.upper() == 'MULTIPOLYGON':
            # The polygon's don't intersect
            return False, union

        else:
            print("--- UNCHECKED FIX IN MERGE ---")
            print(union)


        return False, union











def repairWKT_v2(wkt_str):
    return simplifyWKT_v2(wkt_str).get_simplified_json()



def repairWKT(wkt_str):
    repairs = []

    # Check the syntax and type
    try:
        wkt_obj = wkt.loads(wkt_str)
        if wkt_obj['type'].upper() not in ['POINT', 'LINESTRING', 'POLYGON']:
            shape = shapely.wkt.loads(wkt.dumps(wkt_obj)).convex_hull
            if shape.geom_type.upper() not in ['POINT', 'LINESTRING', 'POLYGON']:
                raise TypeError('Invalid WKT type ({0}): must be Point, LineString, or Polygon'.format(wkt_obj['type']))
            else:
                wkt_obj = wkt.loads(shape.wkt)
                repairs.append({
                    'type': 'CONVEX_HULL',
                    'report': 'Shape was not a point, linestring, or polygon; using the convex hull instead'
                })
    except ValueError as e:
        return { 'error': {'type': 'VALUE', 'report': 'Could not parse WKT: {0}'.format(str(e))} }
    except TypeError as e:
        return { 'error': {'type': 'TYPE', 'report': str(e)} }

    # Do some shapely magic
    def shape_len(shp):
        shp_type = shp.geom_type.upper()
        if shp_type == 'POINT':
            return 1
        if shp_type == 'LINESTRING':
            return len(shp.coords)
        if shp_type == 'POLYGON':
            return len(shp.exterior.coords)
        return None

    original_shape = shapely.wkt.loads(wkt.dumps(wkt_obj))
    tolerance = 0.00001
    attempts = 1
    shape = original_shape.simplify(tolerance, preserve_topology=True)
    while shape_len(shape) > 300 and attempts <= 10:
        attempts += 1
        logging.debug('Shape length still {0}, simplifying further with tolerance {1}'.format(shape_len(shape), tolerance * 5))
        tolerance *= 5
        shape = original_shape.simplify(tolerance, preserve_topology=True)
    if attempts > 10:
        return { 'error': {'type': 'SIMPLIFY', 'report': 'Could not simplify shape after {0} iterations'.format(attempts)} }
    if shape_len(original_shape) != shape_len(shape):
        repairs.append({
            'type': 'SIMPLIFY',
            'report': 'Simplified shape from {0} points to {1} points'.format(shape_len(original_shape), shape_len(shape))
        })
        logging.debug(self.repairs[-1])

    wkt_obj = wkt.loads(shapely.wkt.dumps(shape))


    if wkt_obj['type'] == 'Polygon': # only use the outer perimeter
        coords = wkt_obj['coordinates'][0]
    elif wkt_obj['type'] == 'Point':
        coords = [wkt_obj['coordinates']]
    else:
        coords = wkt_obj['coordinates']

    # Clamp lat to +/-90
    clamped = 0
    for idx, itm in enumerate(coords):
        if coords[idx][1] != sorted((-90, coords[idx][1], 90))[1]:
            coords[idx][1] = sorted((-90, coords[idx][1], 90))[1]
            clamped += 1
    if clamped > 0:
        repairs.append({
            'type': 'CLAMP',
            'report': 'Clamped {0} values to +/-90 latitude'.format(clamped)
        })
        logging.debug(self.repairs[-1])

    # Check for polygon-specific issues
    if wkt_obj['type'] == 'Polygon':
        if coords[0][0] != coords[-1][0] or coords[0][1] != coords[-1][1]:
            coords.append(coords[0])
            repairs.append({
                'type': 'CLOSE',
                'report': 'Closed open polygon'
            })
            logging.debug(self.repairs[-1])

    # Re-assemble the repaired object prior to unwrapping
    if wkt_obj['type'] == 'Polygon':
        wkt_obj['coordinates'] = [coords]
    elif wkt_obj['type'] == 'Point':
        wkt_obj['coordinates'] = coords[0]
    else:
        wkt_obj['coordinates'] = coords

    # Wrap lon to +/-180
    wrapped = 0
    wkt_obj_unwrapped = wkt.loads(wkt.dumps(wkt_obj)) # Save an unwrapped version for later
    for idx, itm in enumerate(coords):
        if abs(((coords[idx][0] + 180) % 360 - 180) - coords[idx][0]) > 0.000001:
            coords[idx][0] = ((coords[idx][0] + 180) % 360 - 180)
            wrapped += 1
    if wrapped > 0:
        repairs.append({
            'type': 'WRAP',
            'report': 'Wrapped {0} values to +/-180 longitude'.format(wrapped)
        })
        logging.debug(self.repairs[-1])

    # Re-assemble the final unwrapped object
    if wkt_obj['type'] == 'Polygon':
        wkt_obj['coordinates'] = [coords]
    elif wkt_obj['type'] == 'Point':
        wkt_obj['coordinates'] = coords[0]
    else:
        wkt_obj['coordinates'] = coords

    if wkt_obj['type'] == 'Polygon':
        # Check polygons for winding order or any CMR-related issues
        cmr_coords = parse_wkt(wkt.dumps(wkt_obj)).split(':')[1].split(',')
        repair = False
        cfg = get_config()
        r = requests.post(cfg['cmr_base'] + cfg['cmr_api'], headers=cfg['cmr_headers'], data={'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1})
        logging.debug({'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
        if r.status_code != 200:
            if 'Please check the order of your points.' in r.text:
                it = iter(cmr_coords)
                rev = reversed(list(zip(it, it)))
                rv = [i for sub in rev for i in sub]
                r = requests.post(cfg['cmr_base'] + cfg['cmr_api'], headers=cfg['cmr_headers'], data={'polygon': ','.join(rv), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
                if r.status_code == 200:
                    repair = True
                else:
                    return { 'error': {'type': 'UNKNOWN', 'report': 'Tried to repair winding order but still getting CMR error: {0}'.format(r.text)} }
            elif 'The polygon boundary intersected itself' in r.text:
                return { 'error': {'type': 'SELF_INTERSECT', 'report': 'Self-intersecting polygon'}}
            else:
                return { 'error': {'type': 'UNKNOWN', 'report': 'Unknown CMR error: {0}'.format(r.text)}}
        if repair:
            repairs.append({'type': 'REVERSE', 'report': 'Reversed polygon winding order'})
            logging.debug(self.repairs[-1])
            wkt_obj['coordinates'][0].reverse()
            wkt_obj_unwrapped['coordinates'][0].reverse()

    # All done
    return {
        'wkt': {
            'wrapped': wkt.dumps(wkt_obj),
            'unwrapped': wkt.dumps(wkt_obj_unwrapped)
        },
        'repairs': repairs
    }

def unwrap_wkt(v):
    logging.debug('=====================unwrap_wkt=============')
    logging.debug(v)
    logging.debug('=====================unwrap_wkt=============')
    return v
