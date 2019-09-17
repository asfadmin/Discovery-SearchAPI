import pytest, sys, os
import shapely


# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import APIUtils as test_file


# Helper method. Used on tests that are expected to return legit responses
def simplify_legit_wkt(test_wkt):
    wkt_simplified = test_file.repairWKT_v2(test_wkt)
    try:
        actual_wrapped = wkt_simplified["wkt"]["wrapped"]
        actual_unwrapped = wkt_simplified["wkt"]["unwrapped"]
        repairs = wkt_simplified["repairs"]
    except KeyError:
        # This means the parse function failed to load the file:
        print("OUTPUT: " + str(wkt))
        assert False
    actual_wrapped = shapely.wkt.loads(actual_wrapped)
    actual_unwrapped = shapely.wkt.loads(actual_unwrapped)

    return actual_wrapped, actual_unwrapped, repairs


class Test_repairWKT():
    resources_root = os.path.join(project_root, "unit_tests", "Resources")
    ###############################
    #   STORAGE OF GENERIC WKT's  #
    ###############################
    long_forked_poly = "POLYGON((58 35,-36 15,65 39,5 -26,29 7.5,-1 15,31 10,58 35))"
    long_forked_poly_unconnected = "POLYGON((58 35,-36 15,65 39,5 -26,29 7.5,-1 15,31 10))"


    def test_mergeTwoPolysToFormAHole(self):
        # These merge to form a polygon w/ a hole between them
        left_donut_side = "POLYGON((12 8,8 6,10 2,14 3,15 0,9 0,7 7,12 10,12 8))"
        right_donut_side = "POLYGON((10 8,14 6,14 4,13 1,13 0,15 4,14.5 7,10 9,10 8))"  
        test_donut = "GEOMETRYCOLLECTION ("+left_donut_side+", "+right_donut_side+")"
        # Get the response:
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(test_donut)
        # Make both strings consistant by loading/dumping with same library:
        expected_result_wkt = "POLYGON ((12 8.1111111111111107, 14.5 7, 15 4, 14.1999999999999993 2.3999999999999999, 15 0, 13 0, 9 0, 7 7, 10 8.8000000000000007, 10 9, 10.1914893617021285 8.9148936170212760, 12 10, 12 8.1111111111111107))"
        expected_result_wkt = shapely.wkt.loads(expected_result_wkt)

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        # Should removing the hole AFTER the merge be a repair?
        assert len(repairs) == 0

    def test_REPAIR_unconnectedPolygon(self):
        # Unconnected poly means the first set of coords do not match the last
        test_unconnected = self.long_forked_poly_unconnected
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(test_unconnected)
        
        expected_result_wkt = self.long_forked_poly
        expected_result_wkt = shapely.wkt.loads(expected_result_wkt)

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        assert len(repairs) == 1
        assert "Closed open polygon" in str(repairs)

    def test_REPAIR_mergeSingleShapesBeforeUnion(self):
        convex_hull_intersects = "MULTIPOLYGON((( 11 5, 16 40, 36 39, 13 43, 11 5)),(( 19 33, 32 25, 47 42, 31 29, 19 33)) )"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(convex_hull_intersects)

        expected_result_wkt = "POLYGON ((11 5, 13 43, 36 39, 35.48418156808803 38.29848693259972, 47 42, 32 25, 27.66666666666667 27.66666666666667, 11 5))"
        expected_result_wkt = shapely.wkt.loads(expected_result_wkt)

        # assert expected_result_wkt == actual_wrapped
        # assert expected_result_wkt == actual_unwrapped

        # add repair?

    # When two shapes touch, but don't intersect. It shouldn't merge them
    # Should convex_hull the total shape:
    def test_zeroPointGeomerty_touchOnce(self):
        poly1 = "POLYGON((20 5, 24 5, 24 10, 20 10, 20 5))"
        poly2 = "POLYGON((20 0, 22 5, 24 0, 22 3, 20 0))"
        two_touching_shapes = "GEOMETRYCOLLECTION("+poly1+","+poly2+")"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(two_touching_shapes)
        expected_result_wkt = "POLYGON ((20 0, 20 10, 24 10, 24 0, 20 0))"
        print(actual_unwrapped)
        # print(repairs)

    # These shapes touch twice, but don't intersect at all. I'm checking if
    # the built in union function is "smart" enough to delete the middle:
    def test_zeroPointGeomerty_touchTwice(self):
        poly1 = "POLYGON((20 0, 21 5, 22 4, 23 5, 24 0, 22 2, 20 0))"
        poly2 = "POLYGON((20 5, 24 5, 24 10, 20 10, 20 5))"
        two_touching_shapes = "GEOMETRYCOLLECTION("+poly1+","+poly2+")"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(two_touching_shapes)

        expected_result_wkt = "POLYGON ((20 0, 21 5, 20 5, 20 10, 24 10, 24 5, 23 5, 24 0, 20 0))"

    # Anything that intersects should throw an error:
    def test_intersectedPoly(self):
        poly = "POLYGON ((20 5, 20 10, 24 10, 24 5, 22 5, 24 0, 22 3, 20 0, 22 5, 20 5))"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(poly)

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

        # Polygon w/ hole: "POLYGON ((12 8.111111111111111, 14.5 7, 15 4, 14.2 2.4, 15 0, 13 0, 9 0, 7 7, 10 8.800000000000001, 10 9, 10.19148936170213 8.914893617021276, 12 10, 12 8.111111111111111), (13.63636363636364 2.909090909090909, 14 4, 14 6, 11 7.5, 8 6, 10 2, 13.63636363636364 2.909090909090909))"
        #      This removes the hole from a union: p = Polygon(union.exterior.coords)
        #      w/out hole: "POLYGON ((12 8.111111111111111, 14.5 7, 15 4, 14.2 2.4, 15 0, 13 0, 9 0, 7 7, 10 8.800000000000001, 10 9, 10.19148936170213 8.914893617021276, 12 10, 12 8.111111111111111))"

        multi_point_1 = "MULTIPOINT ((10 40), (40 30), (20 20), (30 10))"
        multi_point_2 = "MULTIPOINT (10 40, 40 30, 20 20, 30 10)"
        # assert multi_point_1 == multi_point_2

        poly_hole_stretches_out = "MULTIPOLYGON (((20 35, 10 30, 10 10, 30 5, 45 20, 20 35), (30 20, 20 15, 35 35, 30 20)))"

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


        print(MultiPolygonWithHole)
        reparied_str = test_file.repairWKT_v2(MultiPolygonWithHole)
        print(reparied_str)
        return
        reparied_str = test_file.repairWKT_v2(wkt_str)
        reparied_str = test_file.repairWKT_v2(wkt_str2)

