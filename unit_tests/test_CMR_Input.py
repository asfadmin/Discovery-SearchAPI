import sys, os, yaml, json
import pytest, warnings
# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
resources_root = os.path.join(project_root, "unit_tests", "Resources")
sys.path.insert(0, project_root)
import CMR.Input as test_file
import conftest as helpers


# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the parametrize:
list_of_tests = []
yaml_path = os.path.join(project_root, "unit_tests", "test_CMR_Input.yml")
list_of_tests.extend(helpers.loadTestsFromDirectory(yaml_path))

@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachShapeInYaml(json_test, cli_args):
    # left = test itself, right = configs for ALL tests in that file
    test_info = json_test[0]
    file_config = json_test[1]

    test_info = helpers.setupTestFromConfig(test_info, file_config, cli_args)
    helpers.skipTestsIfNecessary(test_info, file_config, cli_args)

    # Create map/dict for which parser to use:
    # Note: Only parsers that accept exactly one val are here
    parsers = {}
    parsers["parse_string"] = test_file.parse_string
    parsers["parse_int"] = test_file.parse_int
    parsers["parse_float"] = test_file.parse_float
    parsers["parse_date"] = test_file.parse_date

    parsers["parse_date_range"] = test_file.parse_date_range
    parsers["parse_int_range"] = test_file.parse_int_range
    parsers["parse_float_range"] = test_file.parse_float_range

    parsers["parse_string_list"] = test_file.parse_string_list
    parsers["parse_int_list"] = test_file.parse_int_list
    parsers["parse_float_list"] = test_file.parse_float_list

    parsers["parse_int_or_range_list"] = test_file.parse_int_or_range_list
    parsers["parse_float_or_range_list"] = test_file.parse_float_or_range_list

    parsers["parse_coord_string"] = test_file.parse_coord_string
    parsers["parse_bbox_string"] = test_file.parse_bbox_string
    parsers["parse_point_string"] = test_file.parse_point_string
    parsers["parse_wkt"] = test_file.parse_wkt

    if "parser" in test_info and "string" in test_info:
        parser = test_info["parser"]
        test_input = test_info["string"]
        val = parsers[parser](test_input)
        if "expected" in test_info:
            assert test_info["expected"] == val, "CMR INPUT FAIL: expected doesn't match output. Test: {0}.".format(test_info["title"])
        else:
            print("TODO: ADD helpfull print-stuff here...")
        print()
        print(val)
        print(type(val))