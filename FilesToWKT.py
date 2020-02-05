from flask import Response
import logging
import json
from geomet import wkt, InvalidGeoJSONException
from io import BytesIO
import shapefile
import zipfile
import api_headers
import os
from APIUtils import repairWKT
from kml2geojson import build_feature_collection as kml2json
import defusedxml.minidom as md
# from defusedxml import DefusedXmlException, DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden, NotSupportedError


class FilesToWKT:

    def __init__(self, request):
        self.request = request  # store the incoming request
        self.errors = []
        # Find out if the user passed us files:
        if 'files' in self.request.files and len(list(self.request.files.getlist('files'))) > 0:
            self.files = self.request.files.getlist("files")
        else:
            self.files = None

    def get_response(self):
        d = api_headers.base(mimetype='application/json')
        resp_dict = self.make_response()
        ###### For backwards compatibility ######################
        if "parsed wkt" in resp_dict:                           #
            repaired_json = repairWKT(resp_dict["parsed wkt"])  #
            for key, val in repaired_json.items():              #
                resp_dict[key] = val                            #
        #########################################################
        return Response(json.dumps(resp_dict, sort_keys=True, indent=4), 200, headers=d)

    def make_response(self):
        if self.files == None:
            self.errors.append({'type': 'POST', 'report': 'No files provided in files= parameter'})
            return {'errors': self.errors }

        # Helper for organizing files into a dict, combining shps/shx, etc.
        def add_file_to_dict(file_dict, full_name, file_stream):
            ext = full_name.split(".")[-1:][0].lower()              # Everything after the last dot.
            file_name = ".".join(full_name.split(".")[:-1])         # Everything before the last dot.

            # SHP'S:
            if ext in ["shp", "shx", "dbf"]:
                # Save shps as {"filename": {"shp": data, "shx": data, "dbf": data}, "file_2.kml": kml_data}
                if file_name not in file_dict:
                    file_dict[file_name] = {}
                file_dict[file_name][ext] = BytesIO(file_stream)
            # BASIC FILES:
            elif ext in ["kml", "geojson"]:
                file_dict[full_name] = BytesIO(file_stream)
            # Else they pass a zip again:
            elif ext in ["zip"]:
                self.errors.append({"type": "FILE_UNZIP", "report": "Cannot unzip double-compressed files. File: '{0}'.".format(full_name)})
            else:
                self.errors.append({"type": "FILE_UNKNOWN", "report": "Ignoring file with unknown extension. File: '{0}'.".format(full_name)})

        # Have to group all shp types together:
        file_dict = {}
        for file in self.files: 
            full_name = file.filename                   # Everything.
            ext = full_name.split(".")[-1:][0].lower()  # Everything after the last dot.

            if ext == "zip":
                # Add each file 
                with BytesIO(file.read()) as zip_f:
                    zip_obj = zipfile.ZipFile(zip_f)
                    parts = zip_obj.namelist()
                    for part_path in parts:
                        # If it's a dir, skip it. ('parts' still contains the files in that dir)
                        if part_path.endswith("/"):
                            continue
                        part_name = os.path.basename(part_path)
                        add_file_to_dict(file_dict, part_name, zip_obj.read(part_path))
            else:
                # Try to add whatever it is:
                add_file_to_dict(file_dict, full_name, file.read())

        # With everything organized in dict, start parsing them:
        wkt_list = []
        for key, val in file_dict.items():
            ext = key.split(".")[-1:][0].lower()
            # If it's a shp set. (Check first, because 'file.kml.shp' will be loaded, and
            #       the key will become 'file.kml'. The val is always a dict for shps tho):
            if isinstance(val, type({})):
                wkt = parse_shapefile(val)
            # Check for each type now:
            elif ext == "geojson":
                wkt = parse_geojson(val)
            elif ext == "kml":
                wkt = parse_kml(val)
            else:
                # This *should* never get hit, but someone might add a new file-type in 'add_file_to_dict' w/out declaring it here.
                self.errors.append({"type": "STREAM_UNKNOWN", "report": "Ignoring file with unknown tag. File: '{0}'".format(key)})
                continue
            # If the parse function returned a json error:
            if isinstance(wkt, type({})) and "error" in wkt:
                # Give the error a better error discription:
                wkt["error"]["report"] += " (Cannot load file: '{0}')".format(key)
                self.errors.append(wkt["error"])
                continue
            else:
                wkt_list.append(wkt)

        if len(wkt_list) == 0:
            return { 'errors': self.errors }
        elif len(wkt_list) == 1:
            full_wkt = wkt_list[0]
        else:
            full_wkt = "GEOMETRYCOLLECTION({0})".format(",".join(wkt_list))

        returned_dict = {"parsed wkt": full_wkt}
        # Only return the 'errors' key IF there are errors...
        if self.errors != []:
            returned_dict['errors'] = self.errors
        return returned_dict
    

# Takes any json, and returns a list of all {"type": x, "coordinates": y} objects 
# found, ignoring anything else in the block
def recurse_find_geojson(json_input):
    if isinstance(json_input, type({})):
        # If it's a dict, try to load the minimal required for a shape.
        # Then recurse on every object, just incase more are nested inside:
        try:
            new_shape = { "type": json_input["type"], "coordinates": json_input["coordinates"] }
            yield new_shape
        except KeyError:
            pass
        for key_value_pair in json_input.items():
            yield from recurse_find_geojson(key_value_pair[1])
    # If it's a list, just loop through it:
    elif isinstance(json_input, type([])):
        for item in json_input:
            yield from recurse_find_geojson(item)

# Takes a json, and returns a possibly-simplified wkt_str
# Used by both parse_geojson, and parse_kml
def json_to_wkt(geojson):
    geojson_list = []
    for new_shape in recurse_find_geojson(geojson):
        geojson_list.append(new_shape)

    if len(geojson_list) == 0:
        return {'error': {'type': 'VALUE', 'report': 'Could not find any shapes inside geojson.'}}
    elif len(geojson_list) == 1:
        wkt_json = geojson_list[0]
    else:
        wkt_json = { 'type': 'GeometryCollection', 'geometries': geojson_list }

    try:
        wkt_str = wkt.dumps(wkt_json)
    except (KeyError, ValueError) as e:
        return {'error': {'type': 'VALUE', 'report': 'Problem converting a shape to string: {0}'.format(str(e))}}
    return wkt_str


def parse_geojson(f):
    try:
        data = f.read()
        geojson = json.loads(data)
    except json.JSONDecodeError as e:
        return {'error': {'type': 'DECODE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    except KeyError as e:
        return {'error': {'type': 'KEY', 'report': 'Missing expected key: {0}'.format(str(e))}}
    except ValueError as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse GeoJSON: {0}'.format(str(e))}}
    return json_to_wkt(geojson)


def parse_kml(f):
    try:
        kml_str = f.read()
        kml_root = md.parseString(kml_str, forbid_dtd=True)
        wkt_json = kml2json(kml_root)
    # All these BUT the type/value errors are for the md.parseString:
    # except (DefusedXmlException, DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden, NotSupportedError, TypeError, ValueError) as e:
    except Exception as e:  
        return {'error': {'type': 'VALUE', 'report': 'Could not parse kml: {0}'.format(str(e))}} 
    return json_to_wkt(wkt_json)

def parse_shapefile(fileset):
    try:
        reader = shapefile.Reader(**fileset)
        shapes = [i.__geo_interface__ for i in reader.shapes()]
    # In the sourcecode, it looks like sometimes the reader throws "Exception":
    except Exception as e:
        return {'error': {'type': 'VALUE', 'report': 'Could not parse shp: {0}'.format(str(e))}}
    wkt_json = {'type':'GeometryCollection', 'geometries': shapes }
    wkt_str = json_to_wkt(wkt_json)
    return wkt_str
