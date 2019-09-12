import logging
from CMR.Input import parse_wkt
from geomet import wkt
from asf_env import get_config
import requests
import shapely.wkt
import shapely.ops
from shapely.geometry import Polygon, MultiPolygon
import re

class simplifyWKT():
    def __init__(self, wkt_str):
        self.shapes = []
        self.repairs = []
        self.wkt_json = wkt.loads(wkt_str)
        self.wkt_str = ""

        # Populate the shapes and repairs variables:
        # (Don't use original json in function for recursiveness)
        self.__simplifyJsonRecursively(self.wkt_json)

        # Turn the list of shapes into a single shape:
        # (also populates the shape variable)
        self.__simplifyListToSingleShape()


    def getShape(self):
        return self.wkt_str

    def getListOfRepairs(self):
        return self.repairs

    # wkt_json can have nested GEOMETRYCOLLECTIONS,
    # This goes inside all of them and populates self.shapes
    # with jsons of broken-down shapes
    ##########
    # TO DO!!!: Add check for poly's not forming a ring
    ##########
    def __simplifyJsonRecursively(self, wkt_json):

        # If GEOMETRY COLLECTION, grab the shapes inside it:
        if wkt_json['type'].upper() == 'GEOMETRYCOLLECTION':
            inner_wkt = wkt_json["geometries"]
            for shape in inner_wkt:
                # Run each shape through again. Could be another geo collection:
                self.__simplifyJsonRecursively(shape)
        # If multipolygon, throw away the holes and add each polygon:
        elif wkt_json['type'].upper() == 'MULTIPOLYGON':
            # For each set of coordinates, create the new poly without the hole:
            for i in range(len(wkt_json["coordinates"])):
                poly = {'type': 'Polygon', 'coordinates': [ wkt_json["coordinates"][i][0] ] }
                self.shapes.append(poly)
        # If supported shape, just add it:
        elif wkt_json['type'].upper() in ['POINT', 'LINESTRING', 'POLYGON']:
            self.shapes.append(wkt_json)
        # Else try to convex_hull whatever it is:
        else:
            # Put every thing above in a try block? Then what's below in the except?
            # Match coords that are nested an unknown number of times:  (i.e. [[3,4],[5,6],[[[7,8],[9,10]]]])
            match_coords = match_coords = r'(\[\s*-?((\d+\.\d*)|(\d*\.\d+)|(\d+))\s*,\s*-?((\d+\.\d*)|(\d*\.\d+)|(\d+))\s*\])'
            coords = re.findall(match_coords,str(wkt_json["coordinates"]))
            # If you couldn't find any points:
            if len(coords) == 0:
                self.repairs.append({
                    'type': 'FAILED_CONVEX_HULL',
                    'report': 'Could not parse points inside unknown shape: {}. Skipping it.'.format(wkt_json['type'])
                })
                logging.debug(self.repairs[-1])
                return

            # Group them together:
            all_coords = []
            for i in range(len(coords)):
                this_set = coords[i][0].strip('][').split(', ')
                all_coords.append([ float(this_set[0]), float(this_set[1]) ])
            
            # Convex_hull and add the new shape:
            MultiPoint = {'type': 'MultiPoint', 'coordinates': all_coords }

            shape = shapely.wkt.loads(wkt.dumps(MultiPoint))
            self.shapes.append(wkt.loads(shapely.wkt.dumps(shape.convex_hull)))
            self.repairs.append({
                'type': 'CONVEX_HULL',
                'report': 'Shape {} was not of a supported type; using it\'s convex hull instead'.format(wkt_json['type'])
            })
            logging.debug(self.repairs[-1])


    def __simplifyListToSingleShape(self):
        # If it's zero, nothing to do:
        if len(self.shapes) == 0:
            self.wkt_str = { 'error': {'type': 'VALUE', 'report': 'Could not parse WKT: No valid shapes found'} }
            return
        # If it's just the one, break out:
        elif len(self.shapes) == 1:
            self.wkt_str = str(shapely.wkt.loads(wkt.dumps(self.shapes[0])))
            return

        # Start dealing with shapelyshapes from here on:
        shapely_shapes = []
        for shape in self.shapes:
            new_shape = shapely.wkt.loads(wkt.dumps(shape))
            shapely_shapes.append(new_shape)
        self.shapes = shapely_shapes

        # Try to simplify List:
        while True:
            merged_helped = self.__repairShapelyList_Merge()
            if len(self.shapes) == 1:
                # Congrats! it worked!
                self.wkt_str = str(shapely.wkt.dumps(self.shapes[0]))
                return
            # convex_hull AFTER merging to fencepost the fix
            convex_hull_helped = self.__repairShapelyList_convexHull()
            # If you got through without those simplifying it, it can't be simplified.
            if not merged_helped and not convex_hull_helped:
                break
        print("Could not be simplified...")
        print("==================================")
        for shape in self.shapes:
            print(str(shape))
        print("==================================")

   
    ##########
    # TO DO!!!: Add check for if a shape is completely inside another, delete it
    ##########
    def __repairShapelyList_Merge(self):
        shapely_shapes = []
        # First check if you can merge it with an existing shape, then add it to the end
        for tmp_shape in self.shapes:
            merged = False
            for i, shp_shape in enumerate(shapely_shapes):
                union = shapely.ops.unary_union([tmp_shape, shp_shape])
                # If you didn't change the type of shape, union successful
                if union.geom_type.upper() in [shp_shape.geom_type.upper(), tmp_shape.geom_type.upper()]:
                    shapely_shapes[i] = union
                    merged = True
                    break
            # Didn't find a place to merge it. Append it to end:
            if merged == False:
                shapely_shapes.append(tmp_shape)
        # If they're the same size, no merge happened.
        if len(self.shapes) == len(shapely_shapes):
            return False
        self.shapes = shapely_shapes
        return True



    def __repairShapelyList_convexHull(self):
        # If shapes not a polygon, try to convex hull it. (i.e. if it's a line with 3 points)
        print(" HITTTT!!!! ")
        modified_list = False
        for i, shape in enumerate(self.shapes):
            # If you're not a poly, AND convex_hulling would modify that shape:
            if shape.geom_type.upper() != 'POLYGON' and shape != shape.convex_hull:
                self.shapes[i] = shape.convex_hull
                modified_list = True
        return modified_list








def repairWKT_v2(wkt_str):
    wkt_repair_class = simplifyWKT(wkt_str)
    print(wkt_repair_class.getShape())
    print(wkt_repair_class.getListOfRepairs())



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
        logging.debug(repairs[-1])

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
        logging.debug(repairs[-1])

    # Check for polygon-specific issues
    if wkt_obj['type'] == 'Polygon':
        if coords[0][0] != coords[-1][0] or coords[0][1] != coords[-1][1]:
            coords.append(coords[0])
            repairs.append({
                'type': 'CLOSE',
                'report': 'Closed open polygon'
            })
            logging.debug(repairs[-1])

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
        logging.debug(repairs[-1])

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
            logging.debug(repairs[-1])
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
