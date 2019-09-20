import logging
from CMR.Input import parse_wkt
from geomet import wkt, InvalidGeoJSONException
from asf_env import get_config
import requests
import shapely.wkt
import shapely.ops
from shapely.geometry import Polygon, LineString, Point
import re



class simplifyWKT_v2():
    def __init__(self, wkt_str):
        self.shapes = []
        self.error = None
        self.repairs = []
        try:
            wkt_json = wkt.loads(wkt_str)
        except (ValueError, InvalidGeoJSONException) as e:
            self.error = { 'error': {'type': 'VALUE', 'report': 'Could not parse WKT: {0}.'.format(str(e))} }
            return
        except TypeError as e:
            self.error =  { 'error': {'type': 'TYPE', 'report': str(e)} }
            return

        # Turn the json into a list of individual shapes:
        # (Populates self.shapes)
        self.__updateShapes(wkt_json)


        # See if a merge is required or not:
        if len(self.shapes) == 0:
            self.error = { 'error': {'type': 'VALUE', 'report': 'Could not parse WKT: No valid shapes found.'} }
            return
        elif len(self.shapes) == 1:
            single_wkt = self.shapes[0]
        else:
            # Else More than one shape. Try to merge them:
            single_wkt = self.__mergeShapelyList(self.shapes)
            if single_wkt == None:
                possible_repair = {'type': 'CONVEX_HULL_INDIVIDUAL', 'report': 'Convex-halled the INDIVIDUAL shapes to merge them together.'}
                for i, shape in enumerate(self.shapes):
                    # 0 = shape, 1 = bool success: (NOT first shape)
                    shape = self.__convexHullShape(shape)
                    self.shapes[i] = shape
                # Now that each shape is convexed hulled, try again
                single_wkt = self.__mergeShapelyList(self.shapes)
                # If it's STILL not possible, just convex hull everything together and return.
                if single_wkt == None:
                    possible_repair = {'type': 'CONVEX_HULL_ALL', 'report': 'Convex-halled ALL the shapes to merge them together.'}
                    all_shapes = shapely.ops.unary_union(self.shapes)
                    # 0 = shape, 1 = bool success: (NOT first shape)
                    single_wkt = self.__convexHullShape(all_shapes)
                self.repairs.append(possible_repair)
                logging.debug(self.repairs[-1])

        # Quick sanity check. No clue if it's actually possible to hit this:
        if single_wkt.geom_type.upper() not in ["POLYGON", "LINESTRING", "POINT"]:
            self.error = {'error': {'type': 'VALUE', 'report': 'Could not simplify WKT down to single shape.'} }
            return

        # Simplify down to the number of points CMR can handle:
        single_wkt = self.__simplifyPoints(single_wkt)
        if single_wkt == None:
            self.error = { 'error': {'type': 'SIMPLIFY', 'report': 'Could not simplify shape past 300 points.'} }
            return
        # Convert that one shape into the strings:
        self.wkt_unwrapped, self.wkt_wrapped = self.__clampAndWrapWKT(single_wkt)

        if single_wkt.geom_type.upper() == "POLYGON":
            # Uses/Modifies wkt_wrapped and wkt_unwrapped:
            self.__runWKTsAgainstCMR()



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
            wkt_json = self.__convexHullShape(wkt_json)
            # If it was able to create a shape from the points:
            if wkt_json != None:
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


    # Takes either a geomet.wkt or shapely.wkt, and returns the convex_hull
    # of the same type
    def __convexHullShape(self, wkt_obj):
        # To convert back at the end if needed:
        converted_from_shapely = False
        if isinstance(wkt_obj, dict):
            wkt_json = wkt_obj
        else:
            wkt_json = wkt.loads(shapely.wkt.dumps(wkt_obj))
            converted_from_shapely = True

        match_coords = match_coords = r'(\[\s*-?((\d+\.\d*)|(\d*\.\d+)|(\d+))\s*,\s*-?((\d+\.\d*)|(\d*\.\d+)|(\d+))\s*\])'
        coords = re.findall(match_coords, str(wkt_json))
        # If you couldn't find any points:
        if len(coords) == 0:
            return None

        all_coords = []
        for i in range(len(coords)):
            # Group 0 = "[ 1.0, 1.0 ]" as a literall string. Convert to list of floats:
            this_set = coords[i][0].strip('][').split(', ')
            all_coords.append([ float(this_set[0]), float(this_set[1]) ])
        # Convex_hull and add the new shape:
        MultiPoint = {'type': 'MultiPoint', 'coordinates': all_coords }
        # Quicky convert to shapely obj for the convex hull:
        shape = shapely.wkt.loads(wkt.dumps(MultiPoint)).convex_hull
        # If they passed in a shapely object, return one. Else return a geojson
        if converted_from_shapely:
            return shape
        else:
            # else convert back to geojson:
            return wkt.loads(shapely.wkt.dumps(shape))

    # Returns the merge of the shapes IF it could get it down to one,
    # else None otherwise
    def __mergeShapelyList(self, shapely_list):
        # Merge the shape, then apply some repairs:
        union = shapely.ops.unary_union(shapely_list)

        if union.geom_type.upper() in ['GEOMETRYCOLLECTION', 'MULTIPOLYGON']:
            # This means there are shapes completely by themselves:
            return None
        # IF only one line, merge returns linestring.
        # IF two+ lines, even if they're connected, merge returns multilinestring
        elif union.geom_type.upper() == 'POLYGON':
            # This removes any holes inside the poly:
            return Polygon(union.exterior.coords)
        elif union.geom_type.upper() == 'LINESTRING':
            return union
        elif union.geom_type.upper() == 'MULTILINESTRING':
            line_merge = shapely.ops.linemerge(union)
            # If it collapsed into one line:
            if line_merge.geom_type.upper() == 'LINESTRING':
                return line_merge
            else:
                return None
        else:
            print("--- UNCHECKED FIX IN MERGE ---")
            print(union)
            return None

    # single_wkt => Shapely object of type ["POLYGON", "LINESTRING", "POINT"]
    def __simplifyPoints(self, single_wkt):
        tolerance = 0.00001
        attempts = 0
        original_num_points = self.__shapeLength(single_wkt)
        # If already less than 300 points, wont enter
        while self.__shapeLength(single_wkt) > 300 and attempts < 10:
            attempts += 1
            logging.debug('Shape length is {0}, simplifying further with tolerance {1}'.format(self.__shapeLength(shape), tolerance ))
            single_wkt = single_wkt.simplify(tolerance, preserve_topology=True)
            # Set the tolerance for the next loop around:
            tolerance *= 5
        # If it didn't work, what calls this method will catch
        #  the None and return an error:
        if self.__shapeLength(single_wkt) > 300:
            return None
        # Tack on the report if needed:
        if attempts > 0:
            self.repairs.append({
                'type': 'SIMPLIFY',
                'report': 'Simplified shape from {0} points to {1} points, after {2} iterations.'.format(original_num_points, self.__shapeLength(single_wkt), attempts)
            })
            logging.debug(self.repairs[-1])
        return single_wkt


    # Do some shapely magic:
    def __shapeLength(self, shp):
        shp_type = shp.geom_type.upper()
        if shp_type == 'POINT':
            return 1
        if shp_type == 'LINESTRING':
            return len(shp.coords)
        if shp_type == 'POLYGON':
            return len(shp.exterior.coords)
        return None

    # single_wkt => Shapely object of type ["POLYGON", "LINESTRING", "POINT"]
    def __clampAndWrapWKT(self, single_wkt):
        # You can't edit coords in shapely. You have to creat a new shape and override:
        wkt_json = wkt.loads(shapely.wkt.dumps(single_wkt))
        # make coords of any shape the format of [[coord, coord],[coord,coord]]:
        if wkt_json["type"].upper() == "POLYGON":
            [coords] = wkt_json["coordinates"]
        elif wkt_json["type"].upper() == "LINESTRING":
            coords = wkt_json["coordinates"]
        elif wkt_json["type"].upper() == "POINT":
            coords = [wkt_json["coordinates"]]

        # Wrap long to +/- 180
        wrapped = 0
        # Clamp lat to +/- 90
        clamped = 0

        new_coords = []
        for i in range(len(coords)):
            x = coords[i][0]
            y = coords[i][1]
            # Longitude:
            if abs(x) > 180:
                wrapped += 1
                x = (coords[i][0] + 180) % 360 - 180
            # Latitude:
            if y > 90:
                clamped += 1
                y = 90
            elif y < -90:
                clamped += 1
                y = -90
            new_coords.append([x,y])
        # Do the reporting:
        if wrapped > 0:
            self.repairs.append({
                'type': 'WRAP',
                'report': 'Wrapped {0} value(s) to +/-180 longitude'.format(wrapped)
            })
            logging.debug(self.repairs[-1])
        if clamped > 0:
            self.repairs.append({
                'type': 'CLAMP',
                'report': 'Clamped {0} value(s) to +/-90 latitude'.format(clamped)
            })
            logging.debug(self.repairs[-1])

        wkt_unwrapped = shapely.wkt.dumps(single_wkt)

        if wkt_json["type"].upper() == "POLYGON":
            wkt_wrapped = shapely.wkt.dumps(Polygon( new_coords ))
            return wkt_unwrapped, wkt_wrapped

        elif wkt_json["type"].upper() == "LINESTRING":
            wkt_wrapped = shapely.wkt.dumps(LineString( new_coords ))
            return wkt_unwrapped, wkt_wrapped

        elif wkt_json["type"].upper() == "POINT":
            wkt_wrapped = shapely.wkt.dumps(Point( new_coords[0] ))
            return wkt_unwrapped, wkt_wrapped

    def __runWKTsAgainstCMR(self):
        wkt_obj_wrapped = wkt.loads(self.wkt_wrapped)
        wkt_obj_unwrapped = wkt.loads(self.wkt_unwrapped)

        # cmr only accepts coords as "x1,y1,x2,y2,x3,y3,...." (No lists)
        cmr_coords = parse_wkt(wkt.dumps(wkt_obj_wrapped)).split(':')[1].split(',')
        cfg = get_config()
        status_code, text = self.__CMRSendRequest(cmr_coords)
        if status_code != 200:
            if 'Please check the order of your points.' in text:
                it = iter(cmr_coords)
                rev = reversed(list(zip(it, it)))
                reversed_coords = [i for sub in rev for i in sub]
                status_code, text = self.__CMRSendRequest(reversed_coords)
                # If switching the coords worked:
                if status_code == 200:
                    wkt_obj_wrapped['coordinates'][0].reverse()
                    wkt_obj_unwrapped['coordinates'][0].reverse()

                    self.repairs.append({
                        'type': 'REVERSE', 
                        'report': 'Reversed polygon winding order'
                        })
                    logging.debug(self.repairs[-1])
                else:
                    self.error = { 'error': {'type': 'UNKNOWN', 'report': 'Tried to repair winding order but still getting CMR error: {0}'.format(text)} }
                    return
            elif 'The polygon boundary intersected itself' in text:
                self.error = { 'error': {'type': 'SELF_INTERSECT', 'report': 'Self-intersecting polygon'}}
                return
            elif 'The shape contained duplicate points' in text:
                # Get the list of points from the error, and list them to the user:
                match_brackets = r'\[(.*?)\]'
                bad_points = re.findall(match_brackets, text)
                self.error = { 'error': {'type': 'DUPLICATE_POINTS', 'report': 'Duplicated or too-close points: {0}'.format(bad_points)}}
            else:
                self.error = { 'error': {'type': 'UNKNOWN', 'report': 'Unknown CMR error: {0}'.format(text)}}     
                return     

        self.wkt_wrapped = wkt.dumps(wkt_obj_wrapped)
        self.wkt_unwrapped = wkt.dumps(wkt_obj_unwrapped)

    def __CMRSendRequest(self, cmr_coords):
        cfg = get_config()
        logging.debug({'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
        r = requests.post(cfg['cmr_base'] + cfg['cmr_api'], headers=cfg['cmr_headers'], data={'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1})
        return r.status_code, r.text













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
        self.repairs.append({
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
