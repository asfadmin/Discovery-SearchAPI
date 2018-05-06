import xml.etree.ElementTree as ET
from datetime import datetime
from jinja2 import Environment, PackageLoader, select_autoescape
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

templateEnv = Environment(
    loader=PackageLoader('search', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

def attr(name):
    return "./AdditionalAttributes/AdditionalAttribute/[Name='" + name + "']/Values/Value"

def parse_cmr_xml(xml):
    root = ET.fromstring(xml)
    results = []
    for result in root.iter('result'):
        for granule in result.iter('Granule'):
            shape = []
            for point in granule.iter('Point'):
                shape.append({'lon': point.findtext('PointLongitude'), 'lat': point.findtext('PointLatitude')})
            results.append({
                'granuleName': granule.findtext("./DataGranule/ProducerGranuleId"),
                'sizeMB': granule.findtext("./DataGranule/SizeMBDataGranule"),
                'processingDate':  granule.findtext("./DataGranule/ProductionDateTime"),
                'startTime':  granule.findtext("./Temporal/RangeDateTime/BeginningDateTime"),
                'stopTime':  granule.findtext("./Temporal/RangeDateTime/EndingDateTime"),
                'absoluteOrbit': granule.findtext("./OrbitCalculatedSpatialDomains/OrbitCalculatedSpatialDomain/OrbitNumber"),
                'platform': granule.findtext(attr('ASF_PLATFORM')),
                'md5': granule.findtext(attr('MD5SUM')),
                'beamMode': granule.findtext(attr('BEAM_MODE_TYPE')),
                'configurationName': granule.findtext(attr('BEAM_MODE_DESC')),
                'bytes': granule.findtext(attr("BYTES")),
                'granuleType':  granule.findtext(attr('GRANULE_TYPE')),
                'sceneDate': granule.findtext(attr('ACQUISITION_DATE')),
                'flightDirection': granule.findtext(attr('ASCENDING_DESCENDING')),
                'thumbnailUrl': granule.findtext(attr('THUMBNAIL_URL')),
                'farEndLat':  granule.findtext(attr('FAR_END_LAT')),
                'farStartLat':  granule.findtext(attr('FAR_START_LAT')),
                'nearStartLat':  granule.findtext(attr('NEAR_START_LAT')),
                'nearEndLat':  granule.findtext(attr('NEAR_END_LAT')),
                'farEndLon':  granule.findtext(attr('FAR_END_LON')),
                'farStartLon':  granule.findtext(attr('FAR_START_LON')),
                'nearStartLon':  granule.findtext(attr('NEAR_START_LON')),
                'nearEndLon':  granule.findtext(attr('NEAR_END_LON')),
                'processingType':  granule.findtext(attr('PROCESSING_LEVEL')),
                'finalFrame':  granule.findtext(attr('CENTER_ESA_FRAME')),
                'centerLat':  granule.findtext(attr('CENTER_LAT')),
                'centerLon':  granule.findtext(attr('CENTER_LON')),
                'polarization':  granule.findtext(attr('POLARIZATION')),
                'faradayRotation':  granule.findtext(attr('FARADAY_ROTATION')),
                'stringFootprint': None,
                'doppler': granule.findtext(attr('DOPPLER')),
                'baselinePerp': granule.findtext(attr('INSAR_BASELINE')),
                'insarStackSize': granule.findtext(attr('INSAR_STACK_SIZE')),
                'processingDescription': granule.findtext(attr('PROCESSING_DESCRIPTION')),
                'product_file_id': None,
                'percentTroposphere': None,
                'frameNumber': granule.findtext(attr('FRAME_NUMBER')),
                'percentCoherence': None,
                'productName': None,
                'masterGranule': None,
                'percentUnwrapped': None,
                'beamSwath': None,
                'insarGrouping': granule.findtext(attr('INSAR_STACK_ID')),
                'offNadirAngle': granule.findtext(attr('OFF_NADIR_ANGLE')),
                'missionName': granule.findtext(attr('MISSION_NAME')),
                'relativeOrbit': granule.findtext(attr('PATH_NUMBER')),
                'flightLine': granule.findtext(attr('FLIGHT_LINE')),
                'processingTypeDisplay': granule.findtext(attr('PROCESSING_TYPE_DISPLAY')),
                'track': None,
                'beamModeType': granule.findtext(attr('BEAM_MODE_TYPE')),
                'processingLevel': granule.findtext(attr('PROCESSING_TYPE')),
                'lookDirection': granule.findtext(attr('LOOK_DIRECTION')),
                'varianceTroposphere': None,
                'slaveGranule': None,
                'sensor': None,
                'fileName': granule.findtext("./OnlineAccessURLs/OnlineAccessURL/URL").split('/')[-1],
                'downloadUrl': granule.findtext("./OnlineAccessURLs/OnlineAccessURL/URL"),
                'browse': granule.findtext("./AssociatedBrowseImageUrls/ProviderBrowseUrl/URL"),
                'shape': shape
            })
    return {'results': results}

def cmr_to_metalink(r):
    products = parse_cmr_xml(r.text)
    template = templateEnv.get_template('metalink.tmpl')
    return template.render(products)

def cmr_to_csv(r):
    products = parse_cmr_xml(r.text)
    template = templateEnv.get_template('csv.tmpl')
    return template.render(products)

def cmr_to_kml(r):
    products = parse_cmr_xml(r.text)
    template = templateEnv.get_template('kml.tmpl')
    return template.render(products, search_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))

def cmr_to_json(r):
    products = parse_cmr_xml(r.text)
    template = templateEnv.get_template('json.tmpl')
    return template.render(products)

def cmr_to_download(r):
    return r