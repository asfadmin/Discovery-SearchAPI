from test_url_manager import test_URL_Manager
from pytest_WKTValidator import test_repair_wkt, test_files_to_wkt
from test_missionList_manager import test_mission_list

def test_URLManagerSearch(test_info, file_conf, cli_args, test_vars):
    test_URL_Manager(test_info, file_conf, cli_args, test_vars)

def test_WKTValidatorEndpoint(test_info, file_conf, cli_args, test_vars):
    test_repair_wkt(test_info, file_conf, cli_args, test_vars)

def test_FilesToWKTEndpoint(test_info, file_conf, cli_args, test_vars):
    test_files_to_wkt(test_info, file_conf, cli_args, test_vars)

def test_MissionListEndpoint(test_info, file_conf, cli_args, test_vars):
	test_mission_list(test_info, file_conf, cli_args, test_vars)
