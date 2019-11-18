import os
import pytest
import conftest as helpers












# Can't do __name__ == __main__ trick. list_of_tests needs to be declared for the @pytest.mark.parametrize:
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__)))
list_of_tests = []

# Get the tests from all *yml* files:
tests_root = os.path.join(project_root, "**", "test_*.yml")
list_of_tests.extend(helpers.loadTestsFromDirectory(tests_root, recurse=True))

# Same, but with *yaml* files now:
tests_root = os.path.join(project_root, "**", "test_*.yaml")
list_of_tests.extend(helpers.loadTestsFromDirectory(tests_root, recurse=True))

@pytest.mark.parametrize("json_test", list_of_tests)
def test_EachShapeInYaml(json_test, cli_args):
	test_info = json_test[0]
	file_config = json_test[1]
	print(test_info)

