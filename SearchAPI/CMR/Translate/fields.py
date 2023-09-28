def attr_path(name):
    return (
        "./AdditionalAttributes/AdditionalAttribute"
        f"[Name='{name}']/Values/Value"
    )

def get_field_paths():
    paths = {
        'absoluteOrbit':            "./OrbitCalculatedSpatialDomains/OrbitCalculatedSpatialDomain/OrbitNumber",
        'ascendingNodeTime':        attr_path('ASC_NODE_TIME'),
        'baselinePerp':             attr_path('INSAR_BASELINE'),
        'beamMode':                 attr_path('BEAM_MODE_TYPE'),
        'beamModeType':             attr_path('BEAM_MODE_TYPE'),
        'bytes':                    attr_path("BYTES"),
        'centerLat':                attr_path('CENTER_LAT'),
        'centerLon':                attr_path('CENTER_LON'),
        'collectionName':           attr_path('MISSION_NAME'),
        'configurationName':        attr_path('BEAM_MODE_DESC'),
        'doppler':                  attr_path('DOPPLER'),
        'downloadUrl':              "./OnlineAccessURLs/OnlineAccessURL/URL",
        'farEndLat':                attr_path('FAR_END_LAT'),
        'farEndLon':                attr_path('FAR_END_LON'),
        'farStartLat':              attr_path('FAR_START_LAT'),
        'farStartLon':              attr_path('FAR_START_LON'),
        'faradayRotation':          attr_path('FARADAY_ROTATION'),
        'finalFrame':               attr_path('CENTER_ESA_FRAME'),
        'firstFrame':               attr_path('CENTER_ESA_FRAME'),
        'flightDirection':          attr_path('ASCENDING_DESCENDING'),
        'flightLine':               attr_path('FLIGHT_LINE'),
        'granuleName':              "./DataGranule/ProducerGranuleId",
        'granuleType':              attr_path('GRANULE_TYPE'),
        'groupID':                  attr_path('GROUP_ID'),
        'insarBaseline':            attr_path('INSAR_BASELINE'),
        'insarGrouping':            attr_path('INSAR_STACK_ID'),
        'insarStackSize':           attr_path('INSAR_STACK_SIZE'),
        'lookDirection':            attr_path('LOOK_DIRECTION'),
        'md5sum':                   attr_path('MD5SUM'),
        'missionName':              attr_path('MISSION_NAME'),
        'nearEndLat':               attr_path('NEAR_END_LAT'),
        'nearEndLon':               attr_path('NEAR_END_LON'),
        'nearStartLat':             attr_path('NEAR_START_LAT'),
        'nearStartLon':             attr_path('NEAR_START_LON'),
        'offNadirAngle':            attr_path('OFF_NADIR_ANGLE'),
        'pointingAngle':            attr_path('POINTING_ANGLE'),
        'polarization':             attr_path('POLARIZATION'),
        'processingDate':           "./DataGranule/ProductionDateTime",
        'processingDescription':    attr_path('PROCESSING_DESCRIPTION'),
        'processingLevel':          attr_path('PROCESSING_TYPE'),
        'processingType':           attr_path('PROCESSING_LEVEL'),
        'processingTypeDisplay':    attr_path('PROCESSING_TYPE_DISPLAY'),
        'productName':              "./DataGranule/ProducerGranuleId",
        'product_file_id':          "./GranuleUR",
        'relativeOrbit':            attr_path('PATH_NUMBER'),
        'sceneDate':                attr_path('ACQUISITION_DATE'),
        'sceneId':                  "./DataGranule/ProducerGranuleId",
        'sensor':                   './Platforms/Platform/Instruments/Instrument/ShortName',
        'sizeMB':                   "./DataGranule/SizeMBDataGranule",
        'startTime':                "./Temporal/RangeDateTime/BeginningDateTime",
        'stopTime':                 "./Temporal/RangeDateTime/EndingDateTime",
        'thumbnailUrl':             attr_path('THUMBNAIL_URL'),
        'track':                    attr_path('PATH_NUMBER'),
        'pgeVersion':               "./PGEVersionClass/PGEVersion",
        'additionalUrls':           "./OnlineAccessURLs",

        # BURST FIELDS
        'absoluteBurstID':          attr_path('BURST_ID_ABSOLUTE'),
        'relativeBurstID':          attr_path('BURST_ID_RELATIVE'),
        'fullBurstID':              attr_path('BURST_ID_FULL'),
        'burstIndex':               attr_path('BURST_INDEX'),
        'azimuthTime':              attr_path('AZIMUTH_TIME'),
        'azimuthAnxTime':           attr_path('AZIMUTH_ANX_TIME'),
        'samplesPerBurst':          attr_path('SAMPLES_PER_BURST'),
        'subswath':                 attr_path('SUBSWATH_NAME'),
        
        # OPERA RTC FIELDS
        'operaBurstID':                  attr_path('OPERA_BURST_ID'),
    }
    return paths
