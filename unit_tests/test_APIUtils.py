import sys, os
from geomet import wkt


# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
resources_root = os.path.join(project_root, "unit_tests", "Resources")
sys.path.insert(0, project_root)
import APIUtils as test_file


# Helper method. Used on tests that are expected to return legit responses
def simplify_legit_wkt(test_wkt):
    wkt_simplified = test_file.repairWKT(test_wkt)
    try:
        actual_wrapped = wkt_simplified["wkt"]["wrapped"]
        actual_unwrapped = wkt_simplified["wkt"]["unwrapped"]
        repairs = wkt_simplified["repairs"]
    except KeyError:
        # This means the parse function failed to load the file:
        print( "Failed wkt: {0}".format(str(test_wkt)) )
        # This WILL fail, but it shows the error on the test screen this way:
        assert str(wkt_simplified) == None

    actual_wrapped = wkt.loads(actual_wrapped)
    actual_unwrapped = wkt.loads(actual_unwrapped)

    return actual_wrapped, actual_unwrapped, repairs

# Helper method. This one assumes something WILL go wrong.
def simplify_NOT_legit_wkt(test_wkt):
    wkt_simplified = test_file.repairWKT(test_wkt)
    try:
        error = wkt_simplified["error"]
    except KeyError:
        # If an error didn't happen, this will fail and print
        # whatever the contents of "error" are:
        assert error == None
    return error

# TESTS TODO:
#   MULTI* shapes
#   Nested GEOMETRIC COLLECTION
#   Simplify number of points repair
#   repairs for convex_hulling single shapes, and whole shape

class Test_repairWKT():
    ###############################
    #   STORAGE OF GENERIC WKT's  #
    ###############################
    # Random single wkt's:
    long_forked_poly = "POLYGON ((58 35, 31 10, -1 15, 29 7.5, 5 -26, 65 39, -36 15, 58 35))"
    long_forked_poly_unconnected = "POLYGON ((58 35, 31 10, -1 15, 29 7.5, 5 -26, 65 39, -36 15))"
    mulidimentional_poly_1 = "POLYGON((27 25 0 0, 102 36 -96 83, 102 46 4 8, 92 61 15 16, 13 41 23 42, 16 30 -73 8, 27 25 0 0))"

    # basics don't need ANY repair work done: (Others may need reversed winding order repair, for example)
    basic_point = "POINT (30 10)"
    basic_linestring = "LINESTRING(13 5, 30 25, 12 42, 22 38, -3 40, 45 -19)"
    basic_poly = "POLYGON((30 10, 40 40, 20 40, 10 20, 30 10))"

    # These merge to form a polygon w/ a hole between them, while the individual polygons don't have holes:
    left_donut_side = "POLYGON((12 8,8 6,10 2,14 3,15 0,9 0,7 7,12 10,12 8))"
    right_donut_side = "POLYGON((10 8,14 6,14 4,13 1,13 0,15 4,14.5 7,10 9,10 8))"  
    test_donut = "GEOMETRYCOLLECTION ("+left_donut_side+", "+right_donut_side+")"


    #############################
    #  NO REPAIRS NEEDED TESTS  #
    #############################
    def test_basicPointWkt(self):
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(self.basic_point)
        expected_result_wkt = wkt.loads(self.basic_point)

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        assert len(repairs) == 0


    def test_basicLineStringWKT(self):
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(self.basic_linestring)
        expected_result_wkt = wkt.loads(self.basic_linestring)

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        assert len(repairs) == 0


    def test_basicPolyWKT(self):
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(self.basic_poly)
        expected_result_wkt = wkt.loads(self.basic_poly)

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        assert len(repairs) == 0


    ##################
    #  TEST REPAIRS  #
    ##################
    def test_REPAIR_unconnectedPolygon(self):
        # Unconnected poly means the first set of coords do not match the last
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(self.long_forked_poly_unconnected)
        # Load the connected poly, reverse the coords:
        expected_result_wkt = wkt.loads(self.long_forked_poly)

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        assert "Closed 1 open polygon(s)" in str(repairs)
        assert len(repairs) == 1


    def test_REPAIR_mergedByConvexHullingIndividual(self):
        convex_hull_intersects = "MULTIPOLYGON((( 11 5, 16 40, 36 39, 13 43, 11 5)),(( 19 33, 32 25, 47 42, 31 29, 19 33)) )"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(convex_hull_intersects)
        expected_result_wkt = wkt.loads("POLYGON ((11 5, 27.6666666666666679 27.6666666666666679, 32 25, 47 42, 35.4841815680880330 38.2984869325997224, 36 39, 13 43, 11 5))")

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        assert "Reversed polygon winding order" in str(repairs)
        assert "Convex-halled the INDIVIDUAL shapes to merge them together" in str(repairs)
        assert len(repairs) == 2


    def test_REPAIR_wrapLongitude(self):
        poly = "POLYGON ((22 22, 9000 8, 120 3, 22 22))"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(poly)
        expected_wrapped = wkt.loads("POLYGON ((22 22, 0 8, 120 3, 22 22))")
        assert expected_wrapped == actual_wrapped
        assert wkt.loads(poly) == actual_unwrapped
        assert "Wrapped 1 value(s) to +/-180 longitude" in str(repairs)
        assert len(repairs) == 1


    def test_REPAIR_clampLatitudePositive(self):
        poly = "POLYGON((-9 6, 48 -20, 25 500, -9 6))"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(poly)
        expected_wrapped = wkt.loads("POLYGON((-9 6, 48 -20, 25 90, -9 6))")
        assert expected_wrapped == actual_wrapped
        assert wkt.loads(poly) == actual_unwrapped
        assert "Clamped 1 value(s) to +/-90 latitude" in str(repairs)
        assert len(repairs) == 1


    def test_REPAIR_clampLatitudeNegative(self):
        poly = "POLYGON((-9 6, 25 -500, 48 -20, -9 6))"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(poly)
        expected_wrapped = wkt.loads("POLYGON((-9 6, 25 -90, 48 -20, -9 6))")
        assert expected_wrapped == actual_wrapped
        assert wkt.loads(poly) == actual_unwrapped
        assert "Clamped 1 value(s) to +/-90 latitude" in str(repairs)
        assert len(repairs) == 1

    def test_REPAIR_multiDimentionalCoords(self):
        poly = self.mulidimentional_poly_1
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(poly)
        expected_unwrapped = wkt.loads("POLYGON((27 25,102 36,102 46,92 61,13 41,16 30,27 25))")
        expected_wrapped = expected_unwrapped
        assert expected_wrapped == actual_wrapped
        assert expected_unwrapped == actual_unwrapped

    ############
    # geomet.wkt fails to load this entirely. Opened a ticket: https://github.com/geomet/geomet/issues/49
    ############
    # def test_REPAIR_removeEmptyShape(self):
    #     empty_line = "LINESTRING EMPTY"
    #     basic_poly = "POLYGON((27 25,102 36,102 46,92 61,13 41,16 30,27 25))"
    #     geocolection = "GEOMETRYCOLLECTION("+basic_poly+","+empty_line+")"
    #     actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(geocolection)

    #     expected_unwrapped = wkt.loads("POLYGON((27 25,102 36,102 46,92 61,13 41,16 30,27 25))")
    #     expected_wrapped = expected_unwrapped
    #     assert expected_wrapped == actual_wrapped
    #     assert expected_unwrapped == actual_unwrapped
    #     print(repairs)

    ####################
    #  ADVANCED TESTS  #
    ####################

    # When two shapes touch, but don't intersect. It shouldn't merge them
    # Should simplify by convex_hulling the shapes together:
    def test_zeroPointGeomerty_touchOnce(self):
        poly1 = "POLYGON((20 5, 24 5, 24 10, 20 10, 20 5))"
        poly2 = "POLYGON((20 0, 22 5, 24 0, 22 3, 20 0))"
        two_touching_shapes = "GEOMETRYCOLLECTION("+poly1+","+poly2+")"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(two_touching_shapes)
        expected_result_wkt = wkt.loads("POLYGON ((20 0, 24 0, 24 10, 20 10, 20 0))")

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        assert "Reversed polygon winding order" in str(repairs)
        assert "Convex-halled ALL the shapes to merge them together" in str(repairs)
        assert len(repairs) == 2


    # These shapes touch twice, but don't intersect at all. Convex_hulling
    # the individual shapes lets the merge succeed, since both shapes then
    # have a whole side touching. (versus the individual single-points):
    def test_zeroPointGeomerty_touchTwice(self):
        poly1 = "POLYGON((20 0, 21 5, 22 4, 23 5, 24 0, 22 2, 20 0))"
        poly2 = "POLYGON((20 5, 24 5, 24 10, 20 10, 20 5))"
        two_touching_shapes = "GEOMETRYCOLLECTION("+poly1+","+poly2+")"

        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(two_touching_shapes)
        expected_result_wkt = wkt.loads("POLYGON ((20 0, 24 0, 23 5, 24 5, 24 10, 20 10, 20 5, 21 5, 20 0))")

        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        assert "Reversed polygon winding order" in str(repairs)
        assert "Convex-halled the INDIVIDUAL shapes to merge them together" in str(repairs)
        assert len(repairs) == 2

    def test_mergeTwoPolysToFormAHole(self):
        # Get the response:
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(self.test_donut)
        # Make both strings consistant by loading/dumping with same library:
        expected_result_wkt = { 'type': 'Polygon', 'coordinates': [[[12.0, 8.11111111111111], [12.0, 10.0], [10.191489361702128, 8.914893617021276], [10.0, 9.0], [10.0, 8.8], [7.0, 7.0], [9.0, 0.0], [13.0, 0.0], [15.0, 0.0], [14.2, 2.4], [15.0, 4.0], [14.5, 7.0], [12.0, 8.11111111111111]]]}
        assert expected_result_wkt == actual_wrapped
        assert expected_result_wkt == actual_unwrapped
        # Should removing the hole AFTER the merge be a repair?
        assert "Reversed polygon winding order" in str(repairs)
        assert len(repairs) == 1



    #################
    #  TEST ERRORS  #
    #################

    # Anything that intersects should throw an error.
    # Here, the "22 5" point is duplicated:
    def test_ERROR_duplicatePointsPoly(self):
        poly = "POLYGON ((20 5, 20 10, 24 10, 24 5, 22 5, 24 0, 22 3, 20 0, 22 5, 20 5))"
        error = simplify_NOT_legit_wkt(poly)
        assert "Duplicated or too-close points" in str(error)

    def test_ERROR_selfIntersectingPoly(self):
        poly = "POLYGON((7 8, 36 38, 11 42, 48 -20,7 8))"
        error = simplify_NOT_legit_wkt(poly)
        assert "Self-intersecting polygon" in str(error)

    def test_ERROR_noValidShapes(self):
        poly = "POLYGON EMPTY"
        error = simplify_NOT_legit_wkt(poly)
        assert "Could not parse WKT: No valid shapes found" in str(error)

