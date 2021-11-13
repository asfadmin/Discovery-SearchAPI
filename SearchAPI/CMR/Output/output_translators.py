from .count import count, req_fields_count
from .csv import cmr_to_csv, req_fields_csv
from .download import cmr_to_download, req_fields_download
from .geojson import cmr_to_geojson, req_fields_geojson
from .json import cmr_to_json, req_fields_json
from .jsonlite import cmr_to_jsonlite, req_fields_jsonlite
from .jsonlite2 import cmr_to_jsonlite2, req_fields_jsonlite2
from .kml import cmr_to_kml, req_fields_kml
from .metalink import cmr_to_metalink, req_fields_metalink

def output_translators():
    return {
        'count':        [count, 'text/plain; charset=utf-8', 'txt', req_fields_count()],
        'csv':          [cmr_to_csv, 'text/csv; charset=utf-8', 'csv', req_fields_csv()],
        'download':     [cmr_to_download, 'text/plain; charset=utf-8', 'py', req_fields_download()],
        'geojson':      [cmr_to_geojson, 'application/geojson; charset=utf-8', 'geojson', req_fields_geojson()],
        'json':         [cmr_to_json, 'application/json; charset=utf-8', 'json', req_fields_json()],
        'jsonlite':     [cmr_to_jsonlite, 'application/json; charset=utf-8', 'json', req_fields_jsonlite()],
        'jsonlite2':    [cmr_to_jsonlite2, 'application/json; charset=utf-8', 'json', req_fields_jsonlite2()],
        'kml':          [cmr_to_kml, 'application/vnd.google-earth.kml+xml; charset=utf-8', 'kmz', req_fields_kml()],
        'metalink':     [cmr_to_metalink, 'application/metalink+xml; charset=utf-8', 'metalink', req_fields_metalink()]
    }
