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
    def checkWKT_NoRepairsNeeded(self, wkt_str):
        wkt_returned = test_file.repairWKT(wkt_str)
        try:
            actual_wrapped = wkt_returned["wkt"]["wrapped"]
            actual_unwrapped = wkt_returned["wkt"]["unwrapped"]
        except KeyError:
            # This means the parse function failed to load the file:
            print("OUTPUT: " + str(wkt))
            assert False

        # Turn "10" into "10.00000...." :
        wkt_str = shapely.wkt.dumps(shapely.wkt.loads(wkt_str))
        assert actual_wrapped == wkt_str
        assert actual_unwrapped == wkt_str

    def test_basicPointWkt(self):
        wkt_str = "POINT (30 10)"
        self.checkWKT_NoRepairsNeeded(wkt_str)

    def test_polygonConeected(self):
        wkt_str = "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))"
        self.checkWKT_NoRepairsNeeded(wkt_str)
        reparied_str = test_file.repairWKT_v2(wkt_str)
        print(reparied_str)

    # def test_polygonNotConnected(self):

    # def test_polyInsideGeoColection(self):

    # def test_MergeHShape(self):





    #############################
    #    REPAIRS NEEDED TESTS   #
    #############################
    def test_polygonUnconeected(self):

        left_donut = "POLYGON((12 8,8 6,10 2,14 3,15 0,9 0,7 7,12 10,12 8))"
        right_donut = "POLYGON((10 8,14 6,14 4,13 1,13 0,15 4,14.5 7,10 9,10 8))"
        # Polygon w/ hole: "POLYGON ((12 8.111111111111111, 14.5 7, 15 4, 14.2 2.4, 15 0, 13 0, 9 0, 7 7, 10 8.800000000000001, 10 9, 10.19148936170213 8.914893617021276, 12 10, 12 8.111111111111111), (13.63636363636364 2.909090909090909, 14 4, 14 6, 11 7.5, 8 6, 10 2, 13.63636363636364 2.909090909090909))"
        #      This removes the hole from a union: p = Polygon(union.exterior.coords)
        #      w/out hole: "POLYGON ((12 8.111111111111111, 14.5 7, 15 4, 14.2 2.4, 15 0, 13 0, 9 0, 7 7, 10 8.800000000000001, 10 9, 10.19148936170213 8.914893617021276, 12 10, 12 8.111111111111111))"

        multi_point_1 = "MULTIPOINT ((10 40), (40 30), (20 20), (30 10))"
        multi_point_2 = "MULTIPOINT (10 40, 40 30, 20 20, 30 10) "
        # assert multi_point_1 == multi_point_2



        long_poly = "POLYGON((58 35,-36.2890625 15,65 39,5.60546875 -26,29 7.5,-1 15,31 10,58 35))"
        wkt_str = "GEOMETRYCOLLECTION ( POINT (40 10), LINESTRING (10 10, 20 20, 10 40), POLYGON ((40 40, 20 45, 45 30, 40 40)))"
        wkt_str2 = "GEOMETRYCOLLECTION ( "+wkt_str+", POINT (40 11) )"
        wkt_str3 = "GEOMETRYCOLLECTION ( POINT (40 11) )"
        JustGeoets = "GEOMETRYCOLLECTION ( GEOMETRYCOLLECTION ( GEOMETRYCOLLECTION ( POINT (40 11) ) ) )"
        reallyNestedWKT = "GEOMETRYCOLLECTION ( "+wkt_str2+", "+wkt_str+",POINT (40 11), POINT (40 40),"+long_poly+",LINESTRING(33 39,35 37,37 36,37 36) )"
        basic_wkt = "POINT (40 11)"
        MultiPolygonWithHole = "MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)),((20 35, 10 30, 10 10, 30 5, 45 20, 20 35),(30 20, 20 15, 20 25, 30 20)))"
        MultiLineWKT = "MULTILINESTRING ((10 10, 20 20, 10 40), (40 40, 30 30, 40 20, 30 10))"

        MultiLineWKTConnected = "MULTILINESTRING ((10 10, 20 20, 10 40, 40 40), (40 40, 30 30, 40 20, 30 10))"
        
        poly1 = "POLYGON((40 40,20 45,-4 20,45 30,40 40))"
        poly2 = "POLYGON((20 35,-8 42,15 33,12 6.5,20 35))"
        # With two points, can't be simplified to polygon. three points can
        line1 = "LINESTRING(12 42,30 25,14 3.14)"

        GeoColection = "GEOMETRYCOLLECTION ( "+left_donut+", "+right_donut+")"

        print(multi_point_1)
        reparied_str = test_file.repairWKT_v2(multi_point_1)

        return
        reparied_str = test_file.repairWKT_v2(wkt_str)
        reparied_str = test_file.repairWKT_v2(wkt_str2)

