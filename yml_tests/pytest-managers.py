from test_url_manager import test_URL_Manager
from test_missionList_manager import test_mission_list
from test_dateParser_manager import test_date_parser
from test_baseline_manager import test_baseline
from test_WKTUtils import test_filesToWKT, test_repairWKT

##########################
## SearchAPI Main tests ##
##########################
def test_URLManagerSearch(**args):
    test_URL_Manager(**args)

def test_MissionListEndpoint(**args):
    test_mission_list(**args)

def test_DateParserEndpoint(**args):
    test_date_parser(**args)

def test_BaselineEndpoint(**args):
    test_baseline(**args)

###########################
## WKTUtils Single tests ##
###########################
def test_FilesToWKTEndpoint(**args):
    test_filesToWKT(**args)

def test_RepairWKTEndpoint(**args):
    test_repairWKT(**args)
