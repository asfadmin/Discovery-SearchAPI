import pytest, sys, os
import shapely


# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import APIUtils as test_file

class Test_repairWKT():
    resources_root = os.path.join(project_root, "test_cameron", "Resources")

    #############################
    #  NO REPAIRS NEEDED TESTS  #
    #############################
    # def checkWKT_NoRepairsNeeded(self, wkt_str):
    #     wkt_returned = test_file.repairWKT(wkt_str)
    #     try:
    #         actual_wrapped = wkt_returned["wkt"]["wrapped"]
    #         actual_unwrapped = wkt_returned["wkt"]["unwrapped"]
    #     except KeyError:
    #         # This means the parse function failed to load the file:
    #         print("OUTPUT: " + str(wkt))
    #         assert False

    #     # Turn "10" into "10.00000...." :
    #     wkt_str = shapely.wkt.dumps(shapely.wkt.loads(wkt_str))
    #     assert actual_wrapped == wkt_str
    #     assert actual_unwrapped == wkt_str

    # def test_basicPointWkt(self):
    #     wkt_str = "POINT (30 10)"
    #     self.checkWKT_NoRepairsNeeded(wkt_str)

    # def test_polygonConeected(self):
    #     wkt_str = "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))"
    #     self.checkWKT_NoRepairsNeeded(wkt_str)
    #     reparied_str = test_file.repairWKT_v2(wkt_str)
    #     print(reparied_str)





    #############################
    #    REPAIRS NEEDED TESTS   #
    #############################
    def test_polygonUnconeected(self):
        long_poly = "POLYGON((58 35,-36.2890625 15,65 39,5.60546875 -26,29 7.5,-1 15,31 10,58 35))"
        wkt_str = "GEOMETRYCOLLECTION ( POINT (40 10), LINESTRING (10 10, 20 20, 10 40), POLYGON ((40 40, 20 45, 45 30, 40 40)))"
        wkt_str2 = "GEOMETRYCOLLECTION ( "+wkt_str+", POINT (40 11) )"
        wkt_str3 = "GEOMETRYCOLLECTION ( POINT (40 11) )"
        JustGeoets = "GEOMETRYCOLLECTION ( GEOMETRYCOLLECTION ( GEOMETRYCOLLECTION ( POINT (40 11) ) ) )"
        reallyNestedWKT = "GEOMETRYCOLLECTION ( "+wkt_str2+", "+wkt_str+",POINT (40 11), POINT (40 40),"+long_poly+",LINESTRING(33 39,35 37,37 36,37 36) )"
        basic_wkt = "POINT (40 11)"
        MultiPolygonWithHole = "MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)),((20 35, 10 30, 10 10, 30 5, 45 20, 20 35),(30 20, 20 15, 20 25, 30 20)))"
        MultiLineWKT = "MULTILINESTRING ((10 10, 20 20, 10 40), (40 40, 30 30, 40 20, 30 10))"
        
        poly1 = "POLYGON((40 40,20 45,-4 20,45 30,40 40))"
        poly2 = "POLYGON((20 35,-8 42,15 33,12 6.5,20 35))"
        # With two points, can't be simplified to polygon. three points can
        line1 = "LINESTRING(12 42,30 25,14 3.14)"

        GeoColection = "GEOMETRYCOLLECTION ( "+poly1+", "+poly2+", "+line1+")"

        print(GeoColection)
        reparied_str = test_file.repairWKT_v2(GeoColection)

        return
        reparied_str = test_file.repairWKT_v2(wkt_str)
        reparied_str = test_file.repairWKT_v2(wkt_str2)

