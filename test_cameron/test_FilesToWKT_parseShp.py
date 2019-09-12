import pytest, sys, os

from io import BytesIO
import shapefile

# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import FilesToWKT as test_file

class Test_parseGeoJson():
    resources_root = os.path.join(project_root, "test_cameron", "Resources")

    #Tests to add:
    #	File names more than 8 char long (legacy systems don't allow it, do we?)

    # This test passes:
    def test_DS2494(self):
    	samerica_path = os.path.join(self.resources_root, "shps_valid", "south_america.shp")

    	file = open(samerica_path, "rb")
    	wkt = test_file.parse_shp(file)
    	# print(wkt)

    	# Works:
    	# file = open(shp_path, "rb")
    	# sf = shapefile.Reader(shp=file)
    	# print(sf.shapeTypeName)



    # The problem with "IllegalArgumentException" is in repairWKT, line 40. It tries to load the polygon, but it doesn't 
    # have connecting begining/end points and throws. Later in that method, it tries to fix this, but
    # it's already thrown by that point.

    # test_canada fails: IllegalArgumentException: Points of LinearRing do not form a closed linestring
    # def test_canada(self):
    # 	canada_path = os.path.join(self.resources_root, "shps_valid", "canada.shp")

    # 	file = open(canada_path, "rb")
    # 	wkt = test_file.parse_shp(file)
    # 	# print(wkt)


    # test_westcoast fails: IllegalArgumentException: Points of LinearRing do not form a closed linestring
    # def test_westcoast(self):
    # 	westcoast_path = os.path.join(self.resources_root, "shps_valid", "westcoast.shp")

    # 	file = open(westcoast_path, "rb")
    # 	wkt = test_file.parse_shp(file)
    # 	# print(wkt)



    # test_minera "fails", but doesn't throw. wkt = "{'error': {'type': 'UNKNOWN', 'report': 'Unknown CMR error: <?xml version="1.0" encoding="UTF-8"?><errors><error>The shape contained duplicate points. Points 1 [lon=-65.3500188421458 lat=90], 2 [lon=-65.3500188421458 lat=90], 3 [lon=-3.123281054198742 lat=90] and 4 [lon=-3.123281054198742 lat=90] were considered equivalent or very close.</error></errors>'}}"
    def test_mineria(self):
    	mineria_path = os.path.join(self.resources_root, "shps_valid", "Area_SAR_Mineria.shp")

    	file = open(mineria_path, "rb")
    	wkt = test_file.parse_shp(file)
    	print(wkt)
