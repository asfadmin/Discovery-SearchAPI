import sys, os
import shapely
from geomet import wkt
# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import FilesToWKT as test_file
import APIUtils as repair_file


def get_wkt_from_kml_file(kml_path):
    file = open(kml_path, "r")
    try:
        wkt_str = test_file.parse_kml(file)
    except Exception as e:
        # This will always fail. This way it shows you what 'e' is in console:
        file.close()
        assert str(e) == None
    file.close()
    return wkt_str

class Test_parseKml():
    resources_root = os.path.join(project_root, "unit_tests", "Resources")
    test_repair = True

    def test_Basic_KML(self):
        kml_path = geojson_path = os.path.join(self.resources_root, "kmls_valid", "Basic_1.kml")
        file = open(kml_path, "r")
        wkt_str = test_file.parse_kml(file)
        expected_wkt = wkt.loads("POLYGON ((-43.7081053964396986 -16.7393321204077985, -43.4120498701856974 -16.7345447923975996, -43.4055558349570987 -16.9702325649037995, -43.7068029641585980 -16.9726376711556988, -43.7081053964396986 -16.7393321204077985))")
        assert wkt.loads(wkt_str) == expected_wkt

        if self.test_repair:
            repaired_wkt = repair_file.repairWKT(wkt_str)
            expected_wkt = {'wkt': {
                                'wrapped': 'POLYGON ((-43.7081053964396986 -16.7393321204077985, -43.7068029641585980 -16.9726376711556988, -43.4055558349570987 -16.9702325649037995, -43.4120498701856974 -16.7345447923975996, -43.7081053964396986 -16.7393321204077985))', 
                                'unwrapped': 'POLYGON ((-43.7081053964396986 -16.7393321204077985, -43.7068029641585980 -16.9726376711556988, -43.4055558349570987 -16.9702325649037995, -43.4120498701856974 -16.7345447923975996, -43.7081053964396986 -16.7393321204077985))'
                            }, 'repairs': [
                                {'type': 'REVERSE', 'report': 'Reversed polygon winding order'}
                            ]
                        }
            assert repaired_wkt['wkt'] == expected_wkt['wkt']
            assert len(repaired_wkt['repairs']) == 1
            assert "Reversed polygon winding order" in str(repaired_wkt['repairs'])

    def test_3D_KML(self):
        kml_path = geojson_path = os.path.join(self.resources_root, "kmls_valid", "3D_coords.kml")
        wkt_str = get_wkt_from_kml_file(kml_path)
        # NOT Repaired! parsers keep the data unmodified, and the repair will drop the 3D coords:
        expected_wkt = wkt.loads("GEOMETRYCOLLECTION (POINT (-122.6819440000000014 45.5200000000000031 0.0000000000000000),POINT (-43.1963890000000035 -22.9083329999999989 0.0000000000000000),POINT (28.9760179999999998 41.0122399999999985 0.0000000000000000),POINT (-21.9333330000000011 64.1333329999999933 0.0000000000000000),POLYGON ((-122.6819440000000014 45.5200000000000031 0.0000000000000000, -43.1963890000000035 -22.9083329999999989 0.0000000000000000, 28.9760179999999998 41.0122399999999985 0.0000000000000000, -21.9333330000000011 64.1333329999999933 0.0000000000000000, -122.6819440000000014 45.5200000000000031 0.0000000000000000)))")
        assert wkt.loads(wkt_str) == expected_wkt

        if self.test_repair:
            repaired_wkt = repair_file.repairWKT(wkt_str)
            expected_wkt = {'wkt': {
                                'wrapped': 'POLYGON ((-43.1963890000000035 -22.9083329999999989, 28.9760179999999998 41.0122399999999985, -21.9333330000000011 64.1333329999999933, -122.6819440000000014 45.5200000000000031, -43.1963890000000035 -22.9083329999999989))', 
                                'unwrapped': 'POLYGON ((-43.1963890000000035 -22.9083329999999989, 28.9760179999999998 41.0122399999999985, -21.9333330000000011 64.1333329999999933, -122.6819440000000014 45.5200000000000031, -43.1963890000000035 -22.9083329999999989))'
                            }, 'repairs': [
                                {'type': 'POINT_MERGE', 'report': '4 points found. Grouping them and using their convex hull instead'}, 
                                {'type': 'MULTIDEMENTIONAL_COORDS', 'report': '5 shape(s) used multidimentional coords. Truncated to 2D'}, 
                                {'type': 'REVERSE', 'report': 'Reversed polygon winding order'}
                            ]
                        }
            assert repaired_wkt['wkt'] == expected_wkt['wkt']
            assert len(repaired_wkt['repairs']) == 3
            assert 'Multiple points found: 4. Grouping them and using their convex hull instead' in str(repaired_wkt['repairs'])
            assert 'Shape(s) that used multidimentional coords: 5. Truncated to 2D' in str(repaired_wkt['repairs'])
            assert 'Reversed polygon winding order' in str(repaired_wkt['repairs'])





