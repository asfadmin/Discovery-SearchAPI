import logging
from CMR.Input import parse_wkt
from geomet import wkt, InvalidGeoJSONException
from asf_env import get_config
import requests
import shapely.wkt
import shapely.ops
from shapely.geometry import Polygon, LineString, Point
import re
import json
from sklearn.neighbors import NearestNeighbors
import numpy as np

class simplifyWKT():
    def __init__(self, wkt_str):
        self.shapes = []
        self.error = None
        self.repairs = []
        # I use this in a couple areas. It matches things like: .5, 6e-6, -9. etc.
        self.regex_digit = r"(-?(((\d+\.\d+|\d+)(e-?\d+)?)|(\d+\.|\.\d+)))"

        # wkt.loads doesn't like 3D/4D tags, BUT it loads the coords just fine:
        wkt_str = wkt_str.upper()
        wkt_str = wkt_str.replace(" Z", " ")
        wkt_str = wkt_str.replace(" M", " ")
        wkt_str = wkt_str.replace(" ZM", " ")

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
        self.__splitApartShapes(wkt_json)
        self.shapes, self.repairs = self.__repairEachJsonShape(self.shapes)
        self.shapes = self.__jsonToShapely(self.shapes)

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
                possible_repair = {'type': 'CONVEX_HULL_INDIVIDUAL', 'report': 'Unconnected shapes: Convex-halled each INDIVIDUAL shape to merge them together.'}
                for i, shape in enumerate(self.shapes):
                    shape = self.__convexHullShape(shape)
                    self.shapes[i] = shape
                # Now that each shape is convexed hulled, try again
                single_wkt = self.__mergeShapelyList(self.shapes)
                # If it's STILL not possible, just convex hull everything together.
                if single_wkt == None:
                    possible_repair = {'type': 'CONVEX_HULL_ALL', 'report': 'Unconnected shapes: Convex-halled ALL the shapes together.'}
                    all_shapes = shapely.ops.unary_union(self.shapes)
                    # 0 = shape, 1 = bool success: (NOT first shape)
                    single_wkt = self.__convexHullShape(all_shapes)
                self.repairs.append(possible_repair)
                logging.debug(self.repairs[-1])

 
        self.wkt_unwrapped, self.wkt_wrapped = self.__repairMergedWKT(single_wkt)
        # If the repairMergedWkt hit an error:
        if self.error != None:
            return        

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
    def __splitApartShapes(self, wkt_json):
        # If GEOMETRY COLLECTION, grab the shapes inside it:
        if wkt_json['type'].upper() == 'GEOMETRYCOLLECTION':
            # If empty set:
            if len(wkt_json["geometries"]) == 0:
                return
            inner_wkt = wkt_json["geometries"]
            for shape in inner_wkt:
                # Run each shape through again. Did this way because "shape" might be another GeometryCollection:
                self.__splitApartShapes(shape)

        # If empty shape:
        elif len(wkt_json["coordinates"]) == 0:
            return
        # Else if one of the "MULTI" shapes, send each sub-shape through again:
        # (MULTISTRING, MULTIPOLYGON, MULTIPOINT, MULTILINESTRING, etc...)
        elif wkt_json['type'].upper()[0:5] == 'MULTI':
            for i in range(len(wkt_json["coordinates"])):
                sub_shape = {'type': wkt_json['type'][5:], 'coordinates':  wkt_json["coordinates"][i]  }
                self.__splitApartShapes(sub_shape)

        # If supported shape, just add it:
        elif wkt_json['type'].upper() in ['POINT', 'LINESTRING', 'POLYGON']:
            if wkt_json not in self.shapes:
                self.shapes.append(wkt_json)
        else: 
            # Append whatever it is as is. Each individual shape gets sent through
            # a repair function anyway before converting it to shapely.
            if wkt_json not in self.shapes:
                self.shapes.append(wkt_json)



    def __repairEachJsonShape(self, list_of_shapes):
        # Wrapper for this at end of function:
        def repairSingleJsonShape(self, shape):
            repair_report = []
            ###########################
            # MULTIDIMENSIONAL_COORDS #
            ###########################
            # Turn all [x,y,z,...] coords into [x,y]:
            # (Other repairs assume 2D coords, Do this first)
            str_coords = str(shape["coordinates"])
            match = re.compile(r"(\[\s*" +self.regex_digit+ r"\s*,\s*" +self.regex_digit+ r"(.*?)\])")
            # for [x,y,z], "\2"=x, "\8"=y. re.sub(match_regex, replace_with, whole_string):
            str_coords = re.sub(match,r'[\2,\8]',str_coords)

            json_coords = json.loads(str_coords)
            if json_coords != shape["coordinates"]:
                repair_report.append("FIXED_DIMENTIONS")
                shape['coordinates'] = json_coords

            ###########
            ### BEGIN specific shape fixes:
            ###########
            if shape['type'].upper() not in ['POINT', 'LINESTRING', 'POLYGON']:
                #################
                #  Convex_Hull  #
                #################
                # If not a CMR supported shape, convex hull it:
                shape = self.__convexHullShape(shape)
                if shape != None:
                    repair_report.append({
                        'type': 'CONVEX_HULL',
                        'report': 'Shape {} was not of a supported type; using it\'s convex hull instead'.format(shape['type'])
                    })
                    logging.debug(repair_report[-1])
                else:
                    failed_report = {
                        'type': 'CONVEX_HULL_FAILED',
                        'report': 'Could not parse points inside unknown shape: {}. Skipping it.'.format(shape['type'])
                    }
                    logging.debug(failed_report)
                    return None, [failed_report]

            elif shape['type'].upper() == 'POLYGON':
                #################
                # CLOSE POLYGON #
                #################
                # Only grab the first set of coords. (Take out any holes):
                coords = shape['coordinates'][0]
                # If the first set does not equal the last set:
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                    repair_report.append("CLOSED_POLY")
                # Save the coords, connected and w/out holes, back to the shape
                shape['coordinates'] = [coords]
            return shape, repair_report
            ###  END of repairSingleJsonShape() ###

        # Track what was repaired:
        num_multidim_repair = 0
        num_open_polys = 0

        repaired_shapes = []
        repairs_done = []

        list_of_points = []

        for shape in list_of_shapes:
            shape, repairs = repairSingleJsonShape(self, shape)
            # Shape stuff:
            if shape != None:
                if shape['type'].upper() == 'POINT':
                    list_of_points.append(shape)
                else:
                    repaired_shapes.append(shape)
            # Repairs stuff:
            for repair in repairs:
                if repair == "CLOSED_POLY":
                    num_open_polys += 1
                elif repair == "FIXED_DIMENTIONS":
                    num_multidim_repair += 1
                # Else it IS the repair jsonblock:
                else:
                    repairs_done.append(repair)
                

        # Combine all the points to a single shape and add it:
        if len(list_of_points) == 1:
            repaired_shapes.append(list_of_points[0])
        elif len(list_of_points) > 1:
            new_shape = self.__convexHullShape(list_of_points)
            repaired_shapes.append(new_shape)
            repairs_done.append({
                                'type': 'POINT_MERGE', 
                                'report': 'Multiple points found: {0}. Grouping them and using their convex hull instead'.format(len(list_of_points))
                                })
            logging.debug(repairs_done[-1])

        # Now, add the repairs that would normally flood the user:
        ### CLOSED POLY:
        if num_open_polys > 0:
            repairs_done.append({
                'type': 'CLOSE',
                'report': 'Closed {0} open polygon(s)'.format(num_open_polys)
            })
            logging.debug(repairs_done[-1])

        ### MULTIDEMENTIONAL SHAPES:
        if num_multidim_repair > 0:
            repairs_done.append({
                'type': 'MULTIDEMENTIONAL_COORDS',
                'report': 'Shape(s) that used multidimentional coords: {0}. Truncated to 2D'.format(num_multidim_repair)
            })
            logging.debug(repairs_done[-1])

        return repaired_shapes, repairs_done



    # Returns the same type of obj as wkt_obj (either geomet.wkt, or shapely.wkt)
    # Can take in a list of objs, BUT ALL items in the list are assumed to be same type.
    # (If for whatever reason there's both, shapely is the default return).
    def __convexHullShape(self, wkt_obj):
        # To convert back at the end if needed:
        converted_from_shapely = False
        wkt_shapely = []
        # If you passed it a single geomet.wkt or shapely.wkt:
        if not isinstance(wkt_obj, type([])):
            wkt_obj = [wkt_obj]
        for item in wkt_obj:
            # If a json / geojson:
            if isinstance(item, type({})):
                wkt_shapely.append(shapely.wkt.loads(wkt.dumps(item)))
            # Else you got it from shapely:
            elif getattr(item, "geom_type", None) != None:
                converted_from_shapely = True
                wkt_shapely.append(item)
        # Check for simple case:
        if len(wkt_shapely) == 1 and wkt_shapely[0].geom_type.upper() in ["POINT","MULTIPOINT","LINESTRING","POLYGON"]:
            hulled_shape = wkt_shapely[0].convex_hull
            return hulled_shape if converted_from_shapely else wkt.loads(shapely.wkt.dumps(hulled_shape))
        # Have to merge the coords:
        wkt_json = [wkt.loads(shapely.wkt.dumps(shape)) for shape in wkt_shapely]
        all_coords = self.__getAllCoords(wkt_json)
        if len(all_coords) == 0:
            return None

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

    def __jsonToShapely(self, list_of_shapes):
        shapely_shapes = []
        for shape in list_of_shapes:
            shape = shapely.wkt.loads(wkt.dumps(shape))
            shapely_shapes.append(shape)
        return shapely_shapes

    # Returns the merge of the shapes IF it could get it down to one,
    # else None otherwise
    def __mergeShapelyList(self, shapely_list):
        # Merge the shape, then apply some repairs:
        union = shapely.ops.unary_union(shapely_list)

        if union.geom_type.upper() in ['GEOMETRYCOLLECTION', 'MULTIPOLYGON']:
            # This means there are shapes completely by themselves:
            return None
        elif union.geom_type.upper() == 'POLYGON':
            # This removes any holes inside the poly:
            return Polygon(union.exterior.coords)
        elif union.geom_type.upper() in ['LINESTRING', 'POINT']:
            return union
        elif union.geom_type.upper() == 'MULTILINESTRING':
            # IF only one line, merge returns linestring.
            # IF two+ lines, even if they're connected, merge returns multilinestring
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

    # Takes either a list, or single geomet/shapely wkt, and returns a unique list of points:
    def __getAllCoords(self, wkt_obj):
        if not isinstance(wkt, type([])):
            wkt_obj = [wkt_obj]

        for i, single_shape in enumerate(wkt_obj):
            # If the shape is from shapely:
            if getattr(single_shape, "geom_type", None) != None:
                wkt_obj[i] = wkt.loads(shapely.wkt.dumps(single_shape))

        match_coords = r'(\[\s*' +self.regex_digit+ r'\s*,\s*' +self.regex_digit+ r'\s*\])'
        coords = re.findall(match_coords, str(wkt_obj))

        all_coords = []
        for i in range(len(coords)):
            # Group 0 = "[ 1.0, 1.0 ]" as a literall string. Convert to list of floats:
            this_coord = coords[i][0].strip('][').split(', ')
            this_coord = [ float(this_coord[0]), float(this_coord[1]) ]
            if this_coord not in all_coords:
                all_coords.append(this_coord)
        return all_coords

    # shapely_wkt => Shapely object of type ["POLYGON", "LINESTRING", "POINT"]
    def __repairMergedWKT(self, single_wkt):
        ## Helper functions (Code at end of these):
        # First, it clamps the values, simplifies the points, THEN wraps and 
        #       returns wrapped/unwrapped strings 
        def getCoords(wkt_json):
            # make coords of any shape the format of [[coord, coord],[coord,coord]]:
            if wkt_json["type"].upper() == "POLYGON":
                [coords] = wkt_json["coordinates"]
            elif wkt_json["type"].upper() == "LINESTRING":
                coords = wkt_json["coordinates"]
            elif wkt_json["type"].upper() == "POINT":
                coords = [wkt_json["coordinates"]]
            return coords

        def getJsonWKT(str_type, coords):
            if str_type.upper() == "POLYGON":
                new_shape = shapely.wkt.dumps(Polygon( coords ))
            elif str_type.upper() == "LINESTRING":
                new_shape = shapely.wkt.dumps(LineString( coords ))
            elif str_type.upper() == "POINT":
                new_shape = shapely.wkt.dumps(Point( coords[0] ))
            return wkt.loads(new_shape)

        def getClampedCoords(wkt_json):
            # num_coords out of lat +/- 90
            clamped = 0
            new_coords = []
            old_coords = getCoords(wkt_json)
            for i in range(len(old_coords)):
                x = old_coords[i][0]
                y = old_coords[i][1]
                if y > 90:
                    y = 90
                    clamped += 1
                elif y < -90:
                    y = -90
                    clamped += 1
                new_coords.append([x,y])
            if clamped > 0:
                self.repairs.append({
                    'type': 'CLAMP',
                    'report': 'Clamped {0} value(s) to +/-90 latitude'.format(clamped)
                })
                logging.debug(self.repairs[-1])
            return getJsonWKT(wkt_json['type'], new_coords)

        def getWrappedCoords(wkt_json):
            # num_coords out of long +/- 90
            wrapped = 0
            new_coords = []
            old_coords = getCoords(wkt_json)
            for i in range(len(old_coords)):
                x = old_coords[i][0]
                y = old_coords[i][1]
                if abs(x) > 180:
                    wrapped += 1
                    x = (x + 180) % 360 - 180
                new_coords.append([x,y])
            if wrapped > 0:
                self.repairs.append({
                    'type': 'WRAP',
                    'report': 'Wrapped {0} value(s) to +/-180 longitude'.format(wrapped)
                })
                logging.debug(self.repairs[-1])
            return getJsonWKT(wkt_json['type'], new_coords)

        def simplifyPoints(wkt_json):
            def getClosestPointDist(wkt_json):
                # Modified from: https://stackoverflow.com/questions/45127141/find-the-nearest-point-in-distance-for-all-the-points-in-the-dataset-python
                def distance(p1, p2):
                    lon1, lat1 = p1
                    lon2, lat2 = p2
                    # Convert to radians:
                    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
                    # haversine formula
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1
                    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
                    c = 2 * np.arcsin(np.sqrt(a))
                    km = 6367 * c
                    return km

                ## getClosestPointDist START:
                points = self.__getAllCoords(wkt_json)
                if len(points) < 2:
                    return float("inf")
                nbrs = NearestNeighbors(n_neighbors=2, metric=distance).fit(points)
                distances, indices = nbrs.kneighbors(points)
                distances = distances.tolist()
                #Throw away unneeded data in distances:
                for i, dist in enumerate(distances):
                    distances[i] = dist[1]
                return min(distances)

            ## simplifyPoints START
            tolerance = 0.00001
            attempts = 0
            org_num_points = len(getCoords(wkt_json))
            current_num_points = org_num_points
            closest_distance = getClosestPointDist(wkt_json)
            wkt_shapely = shapely.wkt.loads(wkt.dumps(wkt_json))
            while (current_num_points > 300 or closest_distance < 0.004) and attempts < 10:
                # Set the tolerance/closest_distance for the next loop around:
                logging.debug('The shape\'s length is {0}, simplifying further with tolerance {1}'.format(current_num_points, tolerance ))
                attempts += 1
                wkt_shapely = wkt_shapely.simplify(tolerance, preserve_topology=True)
                tolerance *= 5
                wkt_json = wkt.loads(shapely.wkt.dumps(wkt_shapely))
                current_num_points = len(getCoords(wkt_json))
                closest_distance = getClosestPointDist(wkt_json)
            # If it couldn't simplify enough:
            # Would add closest_dist check here, but it's unclear *exactly* what that distance is. Just hope CMR accept's it at this point:
            if current_num_points > 300:
                self.error = { 'error': {'type': 'SIMPLIFY', 'report': 'Could not simplify {0} past 300 points. (Got from {1}, to {2})'.format(wkt_shapely.geom_type, org_num_points, current_num_points)} }
                return
            if attempts > 0:
                self.repairs.append({
                    'type': 'SIMPLIFY',
                    'report': 'Simplified shape from {0} points to {1} points, after {2} iterations.'.format(org_num_points, current_num_points, attempts)
                })
                logging.debug(self.repairs[-1])
            return wkt.loads(shapely.wkt.dumps(wkt_shapely))

        ## REPAIR MERGED WKT START:
        # Quick sanity check. No clue if it's actually possible to hit this:
        if single_wkt.geom_type.upper() not in ["POLYGON", "LINESTRING", "POINT"]:
            self.error = {'error': {'type': 'VALUE', 'report': 'Could not simplify WKT down to single shape.'} }
            return
        # You can't edit coords in shapely. You have to create a new shape w/ the new coords:
        wkt_json = wkt.loads(shapely.wkt.dumps(single_wkt))
        wkt_json = getClampedCoords(wkt_json)
        wkt_json = simplifyPoints(wkt_json)
        # Clamp, simplify, *then* wrap, to help simplify be more accuate w/ points outside of poles
        if self.error != None:
            return
        wkt_unwrapped = wkt.dumps(wkt_json)
        wkt_wrapped = wkt.dumps(getWrappedCoords(wkt_json))
        return wkt_unwrapped, wkt_wrapped

    def __runWKTsAgainstCMR(self):
    
        def CMRSendRequest(cmr_coords):
            cfg = get_config()
            # logging.debug({'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1})
            logging.debug({'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
            r = requests.post(cfg['cmr_base'] + cfg['cmr_api'], headers=cfg['cmr_headers'], data={'polygon': ','.join(cmr_coords), 'provider': 'ASF', 'page_size': 1, 'attribute[]': 'string,ASF_PLATFORM,FAKEPLATFORM'})
            return r.status_code, r.text

        # NOTE: Only polygons get sent here. Linestring and point wkt's have already returned.
        wkt_obj_wrapped = wkt.loads(self.wkt_wrapped)
        wkt_obj_unwrapped = wkt.loads(self.wkt_unwrapped)

        cmr_coords = parse_wkt(wkt.dumps(wkt_obj_wrapped)).split(':')[1].split(',')
        status_code, text = CMRSendRequest(cmr_coords)
        if status_code != 200:
            if 'Please check the order of your points.' in text:
                it = iter(cmr_coords)
                rev = reversed(list(zip(it, it)))
                reversed_coords = [i for sub in rev for i in sub]
                status_code, text = CMRSendRequest(reversed_coords)
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
                self.error = { 'error': {'type': 'DUPLICATE_POINTS', 'report': 'Duplicated or too-close points: [{0}]'.format("], [".join(bad_points))}}
            else:
                self.error = { 'error': {'type': 'UNKNOWN', 'report': 'Unknown CMR error: {0}'.format(text)}}     
                return     

        self.wkt_wrapped = wkt.dumps(wkt_obj_wrapped)
        self.wkt_unwrapped = wkt.dumps(wkt_obj_unwrapped)



def repairWKT(wkt_str):
    return simplifyWKT(wkt_str).get_simplified_json()



def unwrap_wkt(v):
    logging.debug('=====================unwrap_wkt=============')
    logging.debug(v)
    logging.debug('=====================unwrap_wkt=============')
    return v
