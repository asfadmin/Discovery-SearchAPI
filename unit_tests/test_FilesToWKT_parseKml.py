import sys, os
import shapely
from geomet import wkt
# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import FilesToWKT as test_file
import APIUtils as repair_file




class Test_parseKml():
    resources_root = os.path.join(project_root, "unit_tests", "Resources")


    def test_Basic_KML(self):
        kml_path = geojson_path = os.path.join(self.resources_root, "kmls_valid", "Basic_1.kml")
        file = open(kml_path, "r")
        wkt_str = test_file.parse_kml(file)
        repaired_wkt = repair_file.repairWKT(wkt_str)
        print(repaired_wkt)

    # def test_3D_KML(self):
    #   kml_path = geojson_path = os.path.join(self.resources_root, "kmls_valid", "3D_coords.kml")
    #   # kml2geojson.main.convert(kml_path, os.path.join(self.resources_root, "test.geojson"))
    #   file = open(kml_path, "r")
    #   wkt_str = test_file.parse_kml(file)
    #   print(wkt_str)


