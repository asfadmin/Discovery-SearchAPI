from .count import count
from .csv import cmr_to_csv
from .download import cmr_to_download
from .geojson import cmr_to_geojson
from .json import cmr_to_json
from .jsonlite import cmr_to_jsonlite
from .jsonlite2 import cmr_to_jsonlite2
from .kml import cmr_to_kml
from .metalink import cmr_to_metalink

def output_translators():
    return {
        'count':        [count, 'text/plain; charset=utf-8', 'txt'],
        'csv':          [cmr_to_csv, 'text/csv; charset=utf-8', 'csv'],
        'download':     [cmr_to_download, 'text/plain; charset=utf-8', 'py'],
        'geojson':      [cmr_to_geojson, 'application/geojson; charset=utf-8', 'geojson'],
        'json':         [cmr_to_json, 'application/json; charset=utf-8', 'json'],
        'jsonlite':     [cmr_to_jsonlite, 'application/json; charset=utf-8', 'json'],
        'jsonlite2':    [cmr_to_jsonlite2, 'application/json; charset=utf-8', 'json'],
        'kml':          [cmr_to_kml, 'application/vnd.google-earth.kml+xml; charset=utf-8', 'kmz'],
        'metalink':     [cmr_to_metalink, 'application/metalink+xml; charset=utf-8', 'metalink']
    }
