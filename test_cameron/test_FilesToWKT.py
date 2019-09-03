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
        # print("---->>> " + str(wkt))
        assert wkt["wkt"]["wrapped"] == 'POLYGON ((100.0000000000000000 0.0000000000000000, 101.0000000000000000 0.0000000000000000, 101.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000))'
        assert wkt["wkt"]["unwrapped"] == 'POLYGON ((100.0000000000000000 0.0000000000000000, 101.0000000000000000 0.0000000000000000, 101.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000))'


    def test_featureCollectionGeometry_2(self):
        geojson_path = os.path.join(self.resources_root, "featureCollectionGeometry_2.geojson")
        file = open(geojson_path, "r")
        wkt = test_file.parse_geojson(file)
        # print("---->>> " + str(wkt))
        assert wkt["wkt"]["wrapped"] == 'POLYGON ((100.0000000000000000 0.0000000000000000, 104.0000000000000000 0.0000000000000000, 105.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000))'
        assert wkt["wkt"]["unwrapped"]== 'POLYGON ((100.0000000000000000 0.0000000000000000, 104.0000000000000000 0.0000000000000000, 105.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000))'

    ## This test fails because the "polygon" only has two points, and throws an error when
    ## parsed inside repairWKT. Should repairWKT handle this case, or should it be fixed
    ## inside parse_geojson? (Ideal fix be converting to line and continuing w/ warning?)
    # def test_featureCollectionGeometryCollection_1(self):
    #     file_path = os.path.join(self.resources_root, "featureCollectionGeometryCollection_1.geojson")
    #     file = open(file_path, "r")
    #     wkt = test_file.parse_geojson(file)
    #     print(wkt)

    # TODO: add test for single geom with "MultiPolygon" type. Currently gets passed into repairWKT.
    # Should maybe covert to multipoint and call convex_hull? Fix in parse_geojson or repairWKT? 

    # TODO: add test for geojson NOT containing geometry tag, just type/coords
    # ie. is this a valid geojson?:
    # {
    #     "type": "MultiPolygon", 
    #     "coordinates": [
    #         [
    #             [[40, 40], [20, 45], [45, 30], [40, 40]]
    #         ], 
    #         [
    #             [[20, 35], [10, 30], [10, 10], [30, 5], [45, 20], [20, 35]], 
    #             [[30, 20], [20, 15], [20, 25], [30, 20]]
    #         ]
    #     ]
    # }
    # easyist fix, wrap everything in { "geometry": file.read() }. Method already handles if
    # geom has no "coordinates" field, and skips over it
