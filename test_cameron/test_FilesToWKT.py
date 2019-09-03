import pytest, sys, os
from geomet import wkt
from shapely.geometry import shape 
import shapely

from geomet import wkt

import json, re

# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import FilesToWKT as test_file

# json recursive method modified from: https://stackoverflow.com/questions/21028979/recursive-iteration-through-nested-json-for-specific-key-in-python
def find_elements(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k.lower() == lookup_key.lower():
                yield v
            else:
                yield from find_elements(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from find_elements(item, lookup_key)


class Test_parseGeoJson():
    resources_root = os.path.join(project_root, "test_cameron", "Resources")

    def test_featureCollectionGeometry_1(self):
        geojson_path = os.path.join(self.resources_root, "featureCollectionGeometry_1.geojson")
        file = open(geojson_path, "r")
        wkt = test_file.parse_geojson(file)
        assert wkt["wkt"]["wrapped"] == 'POLYGON ((100.0000000000000000 0.0000000000000000, 101.0000000000000000 0.0000000000000000, 101.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000))'
        assert wkt["wkt"]["unwrapped"] == 'POLYGON ((100.0000000000000000 0.0000000000000000, 101.0000000000000000 0.0000000000000000, 101.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000))'


    def test_featureCollectionGeometry_2(self):

        geojson_path = os.path.join(self.resources_root, "featureCollectionGeometry_2.geojson")
        file = open(geojson_path, "r")
        print(test_file.parse_geojson(file))
        # geojson = json.loads(file.read())

        # # Add all geometries you find to a list. Could be nested deep inside json:
        # geometry_objs = []

        # # Geometry is just one object
        # for geom in find_elements(geojson, "geometry"):
        #     geometry_objs.append(geom)

        # # Geometries is a list of objects
        # for geometries in find_elements(geojson, "geometries"):
        #     for geom in geometries:
        #         geometry_objs.append(geom)


        # if len(geometry_objs) == 0:
        #     return "Could not find any geometries to convert to wkt."
        # elif len(geometry_objs) == 1:
        #     wkt_str = wkt.dumps(geometry_objs[0])
        #     return repairWKT(wkt_str)
        # else:  # len(geometry_objs) > 1

        #     # Combine all the points of each object into one:
        #     all_coords = "["
        #     for geom in geometry_objs:
        #         match_coords = r'(\[\s*((\d+\.+\d*)|(\d*\.+\d+)|(\d+))\s*,\s*((\d+\.+\d*)|(\d*\.+\d+)|(\d+))\s*\])'
        #         cords = re.findall(match_coords,str(geom["coordinates"]))
        #         for i, cord in enumerate(cords):
        #             # Not sure why this is 2D, maybe a regex fix here.
        #             all_coords += str(cords[i][0]) + ","
        #     # Take off the last cooma, add the last brace:
        #     all_coords = str(all_coords)[0:-1] + "]"
        #     wkt_json = '{"type": "MultiPoint", "properties": {}, "coordinates": ' + all_coords + '}'
        #     wkt_json = json.loads(wkt_json)
        #     # print(shapely.wkt.loads(wkt_json))
        #     # print(wkt_json)
        #     print(shapely.geometry.shape(wkt_json).convex_hull)
        #     return
        #     print(shape(wkt_json))

        #     shape = shapely.wkt.loads(wkt.dumps(wkt_obj)).convex_hull

            #     # print(all_coords)
            # return





            # # Throw everything into a single geometric collection, and convex_hall it:
            # wkt_json = '{"type": "GeometryCollection","geometries": ['
            # for geometry in geometry_objs:
            #     wkt_json += json.dumps(geometry) + ','
            # # take out last ',' then finish the json object:
            # wkt_json = wkt_json[:-1] + ']}'
            # wkt_json = json.loads(wkt_json)
            # print(shape(wkt_json))
            # # print(wkt.dumps(wkt_json))

            # return
            # print(wkt_json)
        # Now you have all the geometries from file. Convert to wkt:

        # wkt = test_file.parse_geojson(file)



    # def test_featureCollectionGeometryCollection(self):
    #     file_path = os.path.join(self.resources_root, "featureCollectionGeometryCollection_1.geojson")
    #     file = open(file_path, "r")
    #     # data = json.loads(file.read())['features'][0]['geometry']
    #     data = test_file.parse_geojson(file)
    #     print(data)
