import pytest, sys, os
import shapely

# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import FilesToWKT as test_file

class Test_parseGeoJson():
    resources_root = os.path.join(project_root, "test_cameron", "Resources")

    def test_Basic_1(self):
        geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_1.geojson")
        file = open(geojson_path, "r")

        expected_wrapped = shapely.wkt.loads("POINT (125.6 10.1)")
        expected_unwrapped = expected_wrapped

        wkt = test_file.parse_geojson(file)
        actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
        actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])

        assert expected_wrapped == actual_wrapped
        assert expected_unwrapped == actual_unwrapped

    def test_Basic_FC_1(self):
        geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_FC_1.geojson")
        file = open(geojson_path, "r")

        expected_wrapped = shapely.wkt.loads("POLYGON ((-44.4291615486145   -10.718908791625154, \
                                                        -43.18777084350587  -10.718908791625154, \
                                                        -43.18777084350587  -7.678180587727013,  \
                                                        -44.4291615486145   -7.678180587727013,  \
                                                        -44.4291615486145   -10.718908791625154 ))")
        expected_unwrapped = expected_wrapped

        wkt = test_file.parse_geojson(file)
        actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
        actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])

        assert expected_wrapped == actual_wrapped
        assert expected_unwrapped == actual_unwrapped

    def test_Basic_FC_2(self):
        geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_FC_2.geojson")
        file = open(geojson_path, "r")

        expected_wrapped = shapely.wkt.loads("POLYGON (( 100.0 0.0, 101.0 0.0, 101.0 1.0, 100.0 1.0, 100.0 0.0 ))")
        expected_unwrapped = expected_wrapped

        wkt = test_file.parse_geojson(file)
        actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
        actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])

        assert expected_wrapped == actual_wrapped
        assert expected_unwrapped == actual_unwrapped

    def test_Basic_FC_3(self):
        geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_FC_3.geojson")
        file = open(geojson_path, "r")

        # This Polygon is reversed to match the repair:
        expected_wrapped = shapely.wkt.loads("POLYGON ((-76.9002014084999956 43.5831678113000009, \
                                                        -76.9002276007999939 43.5832899310000030, \
                                                        -76.8994176375999956 43.5833930601000006, \
                                                        -77.2287060000000025 45.0922740000000033, \
                                                        -80.4371509534999944 44.6942759988000020, \
                                                        -80.0593369429000035 43.3131630924999982, \
                                                        -80.0598828581999982 43.3130937289000002, \
                                                        -80.0249249999999961 43.1852990000000005, \
                                                        -76.9002014084999956 43.5831678113000009))")

        expected_unwrapped = expected_wrapped

        wkt = test_file.parse_geojson(file)
        actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
        actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])

        assert expected_wrapped == actual_wrapped
        assert expected_unwrapped == actual_unwrapped
        assert "'Reversed polygon winding order'" in str(wkt["repairs"])


    # def test_featureCollectionGeometry_2(self):
    #     geojson_path = os.path.join(self.resources_root, "featureCollectionGeometry_2.geojson")
    #     file = open(geojson_path, "r")
    #     wkt = test_file.parse_geojson(file)
    #     # print("---->>> " + str(wkt))
    #     assert wkt["wkt"]["wrapped"] == 'POLYGON ((100.0000000000000000 0.0000000000000000, 104.0000000000000000 0.0000000000000000, 105.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000))'
    #     assert wkt["wkt"]["unwrapped"]== 'POLYGON ((100.0000000000000000 0.0000000000000000, 104.0000000000000000 0.0000000000000000, 105.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000))'

    # def test_UITestsCompile_1(self):
    #     geojson_path = os.path.join(self.resources_root, "UITest_1.geojson")
    #     file = open(geojson_path, "r")
    #     wkt = test_file.parse_geojson(file)
    #     print(wkt)

    # def test_UITestsCompile_2(self):
    #     geojson_path = os.path.join(self.resources_root, "UITest_2.geojson")
    #     file = open(geojson_path, "r")
    #     wkt = test_file.parse_geojson(file)
    #     print(wkt)

    # def test_UITestsCompile_3(self):
    #     geojson_path = os.path.join(self.resources_root, "UITest_3.geojson")
    #     file = open(geojson_path, "r")
    #     wkt = test_file.parse_geojson(file)
    #     print(wkt)

    # def test_UITestsCompile_4(self):
    #     geojson_path = os.path.join(self.resources_root, "UITest_4.geojson")
    #     file = open(geojson_path, "r")
    #     wkt = test_file.parse_geojson(file)
    #     print(wkt)

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
