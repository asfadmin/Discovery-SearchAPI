import sys, os, pytest, yaml, ntpath
from geomet import wkt
import shapely.wkt


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



class RunTestsFromYaml():
    def __init__(self, yaml_path):
        self.yaml_name = ntpath.split(yaml_path)[1]
        self.yaml_path = yaml_path

        # Updates self.unit_tests w/ yaml:
        self.getFileContents()
        if self.unit_tests == None:
            return
        
        # TODO: Add a test-checker here. (make sure expected wkt and 
        #       expected error aren't in same block)

        # Run each test:
        for test in self.unit_tests:
            self.runRepairTest(test)


    def getFileContents(self):
        if not os.path.exists(self.yaml_path):
            pytest.skip("File not Found: " + self.yaml_path)
            self.unit_tests = None
            return
        with open(self.yaml_path, "r") as yaml_file:
            unit_tests = []
            try:
                list_of_tests = yaml.safe_load(yaml_file)
                if list_of_tests == None:
                    pytest.skip("Empty YAML: " + self.yaml_name)
                    self.unit_tests = None
                    return
                # Ditch the names of the test, just grab the rest:
                for test in list_of_tests:
                    unit_tests.append(next(iter(test.values())))
            except (yaml.YAMLError, StopIteration) as e:
                print(e)
            if len(unit_tests) == 0:
                pytest.skip("No tests Found: " + self.yaml_name)
                self.unit_tests = None
                return
            self.unit_tests = unit_tests

    def runRepairTest(self, test_dict):
        test_wkt = test_dict["test wkt"]
        result = test_file.repairWKT(test_wkt)
        # Set expected repair to be a list:
        if "repair" not in test_dict:
            expected_repairs = []
        # Elif they gave a single repair, turn to list:
        elif not isinstance(test_dict["repair"], type([])):
            expected_repairs = [test_dict["repair"]]
        else:
            expected_repairs = test_dict["repair"]

        if "error" in result:
            if "expected error msg" in test_dict:
                assert str(test_dict["expected error msg"]) in str(result["error"])
                print("\nsuccess")
                return
        elif "wkt" in result:
            expected_wkt = False
            if "expected wkt" in test_dict:
                expected_wkt = True
                unwrapped_wkt = wrapped_wkt = test_dict["expected wkt"]
            elif "expected wkt wrapped" in test_dict and "expected wkt unwrapped" in test_dict:
                expected_wkt = True
                unwrapped_wkt = test_dict["expected wkt unwrapped"]
                wrapped_wkt = test_dict["expected wkt wrapped"]
            # If you were able to load what the wkt's are supposed to be, see if they match:
            if expected_wkt:
                # Shapely here because 30 != 30.000000 as strings
                assert shapely.wkt.loads(result["wkt"]["wrapped"]) == shapely.wkt.loads(wrapped_wkt)
                assert shapely.wkt.loads(result["wkt"]["unwrapped"]) == shapely.wkt.loads(unwrapped_wkt)
                for repair in expected_repairs:
                    assert repair in str(result["repairs"])
                assert len(result["repairs"]) == len(expected_repairs)
                print("\nsuccess")
                return
        # What is expected didn't line up with what was returned:
        assert result == False



class Test_repairWKT():
    def test_FileTests(self):
        yaml_name = os.path.splitext(os.path.basename(__file__))[0]+".yml"
        yaml_path = os.path.join(project_root, "unit_tests", yaml_name)
        RunTestsFromYaml(yaml_path)
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



    ##################
    #  TEST REPAIRS  #
    ##################



    def test_REPAIR_wrapLongitude(self):
        poly = "POLYGON ((22 22, 9000 8, 120 3, 22 22))"
        actual_wrapped, actual_unwrapped, repairs = simplify_legit_wkt(poly)
        expected_wrapped = wkt.loads("POLYGON ((22 22, 0 8, 120 3, 22 22))")
        assert expected_wrapped == actual_wrapped
        assert wkt.loads(poly) == actual_unwrapped
        assert "Wrapped 1 value(s) to +/-180 longitude" in str(repairs)
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

    ##### geomet.wkt fails to load this entirely. Opened a ticket: https://github.com/geomet/geomet/issues/49
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
        assert "Unconnected shapes: Convex-halled ALL the shapes together" in str(repairs)
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
        assert "Unconnected shapes: Convex-halled each INDIVIDUAL shape to merge them together" in str(repairs)
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

    def test_ERROR_dontPassWKT(self):
        poly = "Totally a ligit poly...."
        error = simplify_NOT_legit_wkt(poly)
        assert "Could not parse WKT" in str(error)

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

