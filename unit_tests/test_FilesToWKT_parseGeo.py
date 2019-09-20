import pytest, sys, os
import shapely
from geomet import wkt


# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import FilesToWKT as test_file
import APIUtils as repair_file

def get_wkt_from_file(geojson_path):
    file = open(geojson_path, "r")
    try:
        wkt_str = test_file.parse_geojson(file)
    except Exception as e:
        # This will always fail. This way it shows you what 'e' is in console:
        file.close()
        assert str(e) == None
    file.close()
    return wkt_str


class Test_parseGeoJson():
    resources_root = os.path.join(project_root, "unit_tests", "Resources")
    test_repair = True

    

    def test_Multi_FC_Multi_GC_1(self):
        geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Multi-FC_Multi-GC_1.geojson")
        wkt_str = get_wkt_from_file(geojson_path)
        assert wkt_str.replace(" ", "") == "GEOMETRYCOLLECTION (\
                                                POINT (102.0000000000000000 -90.0000000000000000),\
                                                POLYGON ((100.0000000000000000 0.0000000000000000, 101.0000000000000000 0.0000000000000000, 101.0000000000000000 1.0000000000000000, 100.0000000000000000 1.0000000000000000, 100.0000000000000000 0.0000000000000000)),\
                                                LINESTRING (102.0000000000000000 0.0000000000000000, 103.0000000000000000 1.0000000000000000, 104.0000000000000000 0.0000000000000000, 105.0000000000000000 1.0000000000000000),\
                                                POLYGON ((30.0000000000000000 10.0000000000000000, 40.0000000000000000 40.0000000000000000, 20.0000000000000000 40.0000000000000000, 10.0000000000000000 20.0000000000000000, 30.0000000000000000 10.0000000000000000))\
                                            )".replace(" ", "")
        if self.test_repair:
            repaired_wkt = repair_file.repairWKT(wkt_str)
            assert repaired_wkt == {'wkt': {
                    'wrapped': 'POLYGON ((102.0000000000000000 -90.0000000000000000, 105.0000000000000000 1.0000000000000000, 40.0000000000000000 40.0000000000000000, 20.0000000000000000 40.0000000000000000, 10.0000000000000000 20.0000000000000000, 102.0000000000000000 -90.0000000000000000))', 
                    'unwrapped': 'POLYGON ((102.0000000000000000 -90.0000000000000000, 105.0000000000000000 1.0000000000000000, 40.0000000000000000 40.0000000000000000, 20.0000000000000000 40.0000000000000000, 10.0000000000000000 20.0000000000000000, 102.0000000000000000 -90.0000000000000000))'
                    }, 'repairs': [
                        {'type': 'CONVEX_HULL_ALL', 'report': 'Convex-halled ALL the shapes to merge them together.'}, 
                        {'type': 'REVERSE', 'report': 'Reversed polygon winding order'}
                    ]
                }


# class Test_parseGeoJson():
#     resources_root = os.path.join(project_root, "unit_tests", "Resources")

#     def test_Basic_1(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_1.geojson")
#         file = open(geojson_path, "r")

#         expected_wrapped = shapely.wkt.loads("POINT (125.6 10.1)")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped
#         assert len(wkt["repairs"]) == 0


#     def test_Basic_FC_1(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_FC_1.geojson")
#         file = open(geojson_path, "r")

#         expected_wrapped = shapely.wkt.loads("POLYGON ((-44.4291615486145   -10.718908791625154, \
#                                                         -43.18777084350587  -10.718908791625154, \
#                                                         -43.18777084350587  -7.678180587727013,  \
#                                                         -44.4291615486145   -7.678180587727013,  \
#                                                         -44.4291615486145   -10.718908791625154 ))")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped
#         assert len(wkt["repairs"]) == 0


#     def test_Basic_FC_2(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_FC_2.geojson")
#         file = open(geojson_path, "r")

#         expected_wrapped = shapely.wkt.loads("POLYGON (( 100.0 0.0, 101.0 0.0, 101.0 1.0, 100.0 1.0, 100.0 0.0 ))")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped
#         assert len(wkt["repairs"]) == 0

#     def test_Basic_FC_3(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_FC_3.geojson")
#         file = open(geojson_path, "r")

#         # This Polygon is reversed from geojson coords to match the repair:
#         # (Maybe switch to calling repairWKT before loads it? Write repairWKT test suite first maybe)
#         expected_wrapped = shapely.wkt.loads("POLYGON ((-76.9002014084999956 43.5831678113000009, \
#                                                         -76.9002276007999939 43.5832899310000030, \
#                                                         -76.8994176375999956 43.5833930601000006, \
#                                                         -77.2287060000000025 45.0922740000000033, \
#                                                         -80.4371509534999944 44.6942759988000020, \
#                                                         -80.0593369429000035 43.3131630924999982, \
#                                                         -80.0598828581999982 43.3130937289000002, \
#                                                         -80.0249249999999961 43.1852990000000005, \
#                                                         -76.9002014084999956 43.5831678113000009))")

#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped

#         assert "'Reversed polygon winding order'" in str(wkt["repairs"])
#         assert len(wkt["repairs"]) == 1


#     def test_Basic_FC_GC_1(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Basic_FC_GC_1.geojson")
#         file = open(geojson_path, "r")

#         # This Polygon is reversed from geojson coords to match the repair:
#         # (Maybe switch to calling repairWKT before loads it? Write repairWKT test suite first maybe)
#         # There's also a 222.222 coord, which gets clamped to 90.0
#         expected_wrapped = shapely.wkt.loads("POLYGON (( 59.9414062499999929  50.6529433672570875, \
#                                                         -22.2222222222222001  90.0000000000000000, \
#                                                          42.9876543210000008 -42.1234567890000022, \
#                                                          59.9414062499999929  50.6529433672570875))")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped

#         assert "'Reversed polygon winding order'" in str(wkt["repairs"])
#         assert "'Clamped 1 values to +/-90 latitude'" in str(wkt["repairs"])
#         assert len(wkt["repairs"]) == 2


#     def test_Mult_FC_1(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Mult-FC_1.geojson")
#         file = open(geojson_path, "r")

#         # This Polygon is reversed from geojson coords to match the repair:
#         # (Maybe switch to calling repairWKT before loads it? Write repairWKT test suite first maybe)
#         expected_wrapped = shapely.wkt.loads("POLYGON ((100.0000000000000000 0.0000000000000000,  \
#                                                         104.0000000000000000 0.0000000000000000,  \
#                                                         105.0000000000000000 1.0000000000000000,  \
#                                                         100.0000000000000000 1.0000000000000000,  \
#                                                         100.0000000000000000 0.0000000000000000))")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped

#         assert "'Reversed polygon winding order'" in str(wkt["repairs"])
#         assert len(wkt["repairs"]) == 1


#     def test_Mult_FC_2(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Mult-FC_2.geojson")
#         file = open(geojson_path, "r")

#         # This Polygon is reversed from geojson coords to match the repair:
#         # (Maybe switch to calling repairWKT before loads it? Write repairWKT test suite first maybe)
#         expected_wrapped = shapely.wkt.loads("POLYGON (( -16.9684999999999988 61.9093000000000018,  \
#                                                          -14.8582999999999998 65.7498999999999967,  \
#                                                          -20.2379999999999995 66.1474999999999937,  \
#                                                         -142.1903839999999946 69.5018079999999969,  \
#                                                         -142.4324000000000012 69.4928000000000026,  \
#                                                         -148.6021000000000072 69.0464999999999947,  \
#                                                         -147.2113999999999976 67.1431000000000040,  \
#                                                         -144.2897000000000105 65.8091000000000008,  \
#                                                          -16.9684999999999988 61.9093000000000018  ))")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped

#         assert "'Reversed polygon winding order'" in str(wkt["repairs"])
#         assert len(wkt["repairs"]) == 1


#     def test_Mult_FC_3(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Mult-FC_3.geojson")
#         file = open(geojson_path, "r")

#         # This Polygon is reversed from geojson coords to match the repair:
#         # (Maybe switch to calling repairWKT before loads it? Write repairWKT test suite first maybe)
#         expected_wrapped = shapely.wkt.loads("POLYGON (( -28.2486780000000017 59.3261150000000015, \
#                                                          -20.9505160000000004 60.0758399999999995, \
#                                                          -21.7188000000000017 67.4003000000000014, \
#                                                          -23.6677999999999997 71.4705000000000013, \
#                                                          -34.6375999999999991 70.5758000000000010, \
#                                                          -35.1432909999999978 69.2202220000000068, \
#                                                          -28.2486780000000017 59.3261150000000015  ))")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False
    
#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped

#         assert "'Reversed polygon winding order'" in str(wkt["repairs"])
#         assert len(wkt["repairs"]) == 1


#     def test_Multi_FC_Multi_GC_1(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Multi-FC_Multi-GC_1.geojson")
#         file = open(geojson_path, "r")

#         # This Polygon is reversed from geojson coords to match the repair:
#         # (Maybe switch to calling repairWKT before loads it? Write repairWKT test suite first maybe)
#         expected_wrapped = shapely.wkt.loads("POLYGON ((  102.0000000000000000 -90.0000000000000000,  \
#                                                           105.0000000000000000   1.0000000000000000,  \
#                                                            59.9414062499999929  50.6529433672570875,  \
#                                                            13.9414062499999893  50.6529433672570875,  \
#                                                            10.0000000000000000  20.0000000000000000,  \
#                                                           102.0000000000000000 -90.0000000000000000  ))")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped

#         assert "'Reversed polygon winding order'" in str(wkt["repairs"])
#         assert len(wkt["repairs"]) == 1


#     def test_Large_ShovelCreek_1(self):
#         geojson_path = os.path.join(self.resources_root, "geojsons_valid", "Large_ShovelCreek_1.geojson")
#         file = open(geojson_path, "r")

#         # This Polygon is reversed from geojson coords to match the repair:
#         # (Maybe switch to calling repairWKT before loads it? Write repairWKT test suite first maybe)
        expected_wrapped = shapely.wkt.loads("POLYGON ((-148.3959299993289562 65.0200699997649849, \
                                                        -148.3980106195110409 65.0204965142181095, \
                                                        -148.3982428597838350 65.0210416129562532, \
                                                        -148.3992698433036423 65.0212037477765534, \
                                                        -148.4086000003617301 65.0205600005863857, \
                                                        -148.4120399989117516 65.0209999994262375, \
                                                        -148.4207299999012548 65.0234800002692737, \
                                                        -148.4247500012677676 65.0234800002692737, \
                                                        -148.4453999984648362 65.0183899991938574, \
                                                        -148.4595599993492669 65.0134799994893342, \
                                                        -148.4620200014951763 65.0121400016531652, \
                                                        -148.4630200005254608 65.0104799997791929, \
                                                        -148.4664800003919538 65.0073400000214860, \
                                                        -148.4696833359055859 64.9997817550319041, \
                                                        -148.4704800004419951 64.9987799984212984, \
                                                        -148.4771114544675754 64.9957006404234789, \
                                                        -148.4788537666308059 64.9943036456456298, \
                                                        -148.4981470362368157 64.9921685745250102, \
                                                        -148.5039482954938990 64.9909733675179950, \
                                                        -148.5048332384965875 64.9904522082811695, \
                                                        -148.5053359562367064 64.9892181432948064, \
                                                        -148.5042842447928422 64.9883712934228015, \
                                                        -148.5010520624355195 64.9880000746468340, \
                                                        -148.4795349390187198 64.9896601341463906, \
                                                        -148.4745600005192614 64.9870000009652813, \
                                                        -148.4681499989951305 64.9788200008039780, \
                                                        -148.4666722602962068 64.9756643308163007, \
                                                        -148.4661999989870935 64.9727799987507524, \
                                                        -148.4650700005674651 64.9714300002563618, \
                                                        -148.4614782594473752 64.9694266494345811, \
                                                        -148.4423399987343259 64.9644899992069327, \
                                                        -148.4402099999747691 64.9633900014523533, \
                                                        -148.4397849536643434 64.9613377946123478, \
                                                        -148.4351494364052826 64.9523679415206630, \
                                                        -148.4341252896358014 64.9505126137993898, \
                                                        -148.4326677303688200 64.9496741707143315, \
                                                        -148.4101995674040495 64.9510527017309869, \
                                                        -148.3997900949375151 64.9512338569232384, \
                                                        -148.3944654857016587 64.9530024044433958, \
                                                        -148.3806671862040218 64.9545538449551145, \
                                                        -148.3774486833746380 64.9560794757533131, \
                                                        -148.3766577250807472 64.9567594471716916, \
                                                        -148.3766052713925490 64.9572756506082101, \
                                                        -148.3799373699648356 64.9602558336657125, \
                                                        -148.3797688924011879 64.9608554763290726, \
                                                        -148.3804958561739227 64.9622322877459624, \
                                                        -148.3802623363512510 64.9648414903878688, \
                                                        -148.3811571032063910 64.9651714020971554, \
                                                        -148.3824091368976497 64.9678018371475900, \
                                                        -148.3805500006491513 64.9696200002959472, \
                                                        -148.3777400003487799 64.9700099997736515, \
                                                        -148.3746299999464213 64.9698699984164136, \
                                                        -148.3693700688806700 64.9687047436165130, \
                                                        -148.3704556510714667 64.9682484603103489, \
                                                        -148.3728913037886343 64.9658865748895664, \
                                                        -148.3722037716316606 64.9646808145425325, \
                                                        -148.3674836154858383 64.9635048243582105, \
                                                        -148.3631116881271055 64.9611724524043552, \
                                                        -148.3560216693460632 64.9596289393395523, \
                                                        -148.3501949120775691 64.9593625166178867, \
                                                        -148.3483878064930650 64.9588212905809428, \
                                                        -148.3458400418918188 64.9576933562050272, \
                                                        -148.3448217886480336 64.9568446675529572, \
                                                        -148.3438516056189940 64.9551018668819324, \
                                                        -148.3411043373155849 64.9546385100352950, \
                                                        -148.3308052859460986 64.9516617805838337, \
                                                        -148.3299539989040454 64.9493352785815432, \
                                                        -148.3184873025825823 64.9465952409793204, \
                                                        -148.3053740442450703 64.9464641021750140, \
                                                        -148.2865662178005834 64.9496535145616463, \
                                                        -148.2749596864502735 64.9498614171927215, \
                                                        -148.2686122807171785 64.9506506611255077, \
                                                        -148.2618036790968290 64.9518252565086982, \
                                                        -148.2513266589679972 64.9547869836630980, \
                                                        -148.2366640726203570 64.9577905731852070, \
                                                        -148.2150862406504075 64.9575996976046213, \
                                                        -148.2070109946338050 64.9565700187790753, \
                                                        -148.1960149578921744 64.9559500146393134, \
                                                        -148.1889280613700635 64.9548099212650527, \
                                                        -148.1839653054429959 64.9531687275959939, \
                                                        -148.1812561433669373 64.9530914660937810, \
                                                        -148.1748649867185748 64.9544090410292370, \
                                                        -148.1578813335089535 64.9593143298422433, \
                                                        -148.1443847157326275 64.9605109342697347, \
                                                        -148.1443437242970447 64.9615406497661070, \
                                                        -148.1450132864393936 64.9620813519341027, \
                                                        -148.1506507528308987 64.9608928216367758, \
                                                        -148.1546971323086836 64.9610809914342440, \
                                                        -148.1582184182938420 64.9612862655528716, \
                                                        -148.1620292361697011 64.9626071578884421, \
                                                        -148.1672635330180867 64.9633549546196605, \
                                                        -148.1727892764982073 64.9631190394061946, \
                                                        -148.1809728206329453 64.9618033556376417, \
                                                        -148.1848876919788154 64.9604500698655443, \
                                                        -148.1873364715421530 64.9625556654997922, \
                                                        -148.1895612093817647 64.9665053400792658, \
                                                        -148.1906662965232044 64.9695663403994672, \
                                                        -148.1916033697249873 64.9700799179429396, \
                                                        -148.1959102102958354 64.9702766412106598, \
                                                        -148.1978054136118033 64.9699418522814653, \
                                                        -148.2040386421074629 64.9658641113890098, \
                                                        -148.2066731947678306 64.9648937384575333, \
                                                        -148.2207828688719928 64.9626538306828252, \
                                                        -148.2276396310744815 64.9622810638741157, \
                                                        -148.2291398463706571 64.9625942261834552, \
                                                        -148.2297506487523435 64.9642739556523452, \
                                                        -148.2306506883484474 64.9649700425892433, \
                                                        -148.2352217055528740 64.9651862498528772, \
                                                        -148.2402036193674064 64.9743580256115933, \
                                                        -148.2386825868288724 64.9756072945845062, \
                                                        -148.2417614825123735 64.9754818869064934, \
                                                        -148.2443149664528903 64.9749598685245928, \
                                                        -148.2463116575906668 64.9729613569422213, \
                                                        -148.2467704109389217 64.9717268650027222, \
                                                        -148.2484462375841758 64.9711756225914883, \
                                                        -148.2496482195263923 64.9701661598686542, \
                                                        -148.2524017991409551 64.9664391164957920, \
                                                        -148.2517274514557641 64.9624456045626175, \
                                                        -148.2511406226268491 64.9620728167992070, \
                                                        -148.2513296659757884 64.9607451586961702, \
                                                        -148.2479919214058839 64.9596390041717200, \
                                                        -148.2474729558703075 64.9585311483829173, \
                                                        -148.2523550176438221 64.9587670649060556, \
                                                        -148.2604817259266099 64.9547931980584963, \
                                                        -148.2642207789951669 64.9535447109600454, \
                                                        -148.2663159797597814 64.9534998363458840, \
                                                        -148.2691240810352156 64.9517758936473228, \
                                                        -148.2727945177488493 64.9513047913982859, \
                                                        -148.2756123773931165 64.9518339959524837, \
                                                        -148.2763401584014389 64.9524765919406377, \
                                                        -148.2759734710919304 64.9533030895040611, \
                                                        -148.2744004982567674 64.9538894272058087, \
                                                        -148.2721344703762725 64.9543103690030534, \
                                                        -148.2693001966081567 64.9539545113743770, \
                                                        -148.2660163974432805 64.9545060406038033, \
                                                        -148.2658114546717627 64.9548624954430807, \
                                                        -148.2662023813975622 64.9552128105382849, \
                                                        -148.2637095719587137 64.9561424762331399, \
                                                        -148.2639175309057009 64.9567471545867647, \
                                                        -148.2672879897817779 64.9580999963799286, \
                                                        -148.2706965706012454 64.9580493434912114, \
                                                        -148.2722634194083753 64.9613378168767781, \
                                                        -148.2736346765047415 64.9623362914484233, \
                                                        -148.2814739732563964 64.9633255825973492, \
                                                        -148.2888952933091105 64.9622973771532202, \
                                                        -148.2899536041920783 64.9615267069940501, \
                                                        -148.2924390362464351 64.9615839016962013, \
                                                        -148.2965727224135719 64.9608216343950176, \
                                                        -148.2989537146445969 64.9584852535339792, \
                                                        -148.3042951466220813 64.9574858975528855, \
                                                        -148.3060428048679285 64.9554073256983315, \
                                                        -148.3054252301703855 64.9543663967871225, \
                                                        -148.3009733185005530 64.9538078333073372, \
                                                        -148.3012561998749561 64.9537228892669418, \
                                                        -148.3003198090124499 64.9531288166401168, \
                                                        -148.2982891227089226 64.9527188014395165, \
                                                        -148.2980910609560397 64.9520676532907260, \
                                                        -148.2992883031939471 64.9520273310977245, \
                                                        -148.3044398143420040 64.9533349774069961, \
                                                        -148.3086997673322287 64.9525188995969529, \
                                                        -148.3177177901738162 64.9534089804443511, \
                                                        -148.3197081542843421 64.9532370924938505, \
                                                        -148.3213444668044474 64.9540380147751648, \
                                                        -148.3213536764205571 64.9555076924406194, \
                                                        -148.3219742096679852 64.9561272342660345, \
                                                        -148.3238170404954417 64.9564399774802155, \
                                                        -148.3276052062779797 64.9562819301473269, \
                                                        -148.3326199103596821 64.9590344214241782, \
                                                        -148.3327216915481017 64.9604938901934474, \
                                                        -148.3342890995853338 64.9618944891896604, \
                                                        -148.3483806779463521 64.9650919796354742, \
                                                        -148.3502456671206744 64.9650193884249347, \
                                                        -148.3513416559681275 64.9644990726171159, \
                                                        -148.3524610552092327 64.9648474493971548, \
                                                        -148.3530638031058402 64.9657930590435058, \
                                                        -148.3537972405891310 64.9658946830712125, \
                                                        -148.3533126264501902 64.9667118898187823, \
                                                        -148.3539871247477038 64.9672043724693253, \
                                                        -148.3366000007703462 64.9700600004455282, \
                                                        -148.3240800004433879 64.9709599994417886, \
                                                        -148.3165000004860588 64.9725300006302859, \
                                                        -148.3142100003624364 64.9734000002712264, \
                                                        -148.3131390131605940 64.9742897825133241, \
                                                        -148.3138100002264821 64.9752500002452393, \
                                                        -148.3157199989112200 64.9760700005239755, \
                                                        -148.3173927425877139 64.9762821543515656, \
                                                        -148.3187389443419022 64.9782607366494744, \
                                                        -148.3191775248066051 64.9783872248071930, \
                                                        -148.3174808822286934 64.9790146652667318, \
                                                        -148.3183191301725969 64.9794047276087099, \
                                                        -148.3178643739444169 64.9803986955977280, \
                                                        -148.3158305797883258 64.9813393677791851, \
                                                        -148.3106442287358107 64.9817736328733986, \
                                                        -148.3075063283829138 64.9824816181838401, \
                                                        -148.3076899706429685 64.9806403484858492, \
                                                        -148.3041541852749674 64.9802380773779760, \
                                                        -148.3033326487505406 64.9810159284707538, \
                                                        -148.3036090420079915 64.9829224774784961, \
                                                        -148.3029990450748130 64.9838836355551734, \
                                                        -148.3032833225599632 64.9845261490340249, \
                                                        -148.3029986141926031 64.9863499293671794, \
                                                        -148.3001099994984031 64.9861199993564469, \
                                                        -148.2987599970749955 64.9864900001370529, \
                                                        -148.2961399988037101 64.9881499993916805, \
                                                        -148.2910500003476386 64.9937600006438743, \
                                                        -148.2946053050726789 64.9950398635633633, \
                                                        -148.3032105912144516 64.9971819741730314, \
                                                        -148.3180141624833084 64.9991480373126933, \
                                                        -148.3241044886974294 65.0011840212409879, \
                                                        -148.3259799997796051 65.0021799995770948, \
                                                        -148.3312600002647628 65.0080600002661981, \
                                                        -148.3350104396249378 65.0093909718403893, \
                                                        -148.3351465892357339 65.0110022591408097, \
                                                        -148.3339866936152021 65.0117482445950827, \
                                                        -148.3346584324330308 65.0122650046424155, \
                                                        -148.3390489073719039 65.0128177073382858, \
                                                        -148.3440400975958369 65.0127025334402333, \
                                                        -148.3538791959571768 65.0143378623963599, \
                                                        -148.3556942656593662 65.0149613816967644, \
                                                        -148.3611022944769786 65.0135474790486114, \
                                                        -148.3634815618694915 65.0144538509106837, \
                                                        -148.3668481362572891 65.0130203280606906, \
                                                        -148.3708081886806553 65.0130458928654207, \
                                                        -148.3721097764454839 65.0140089866379185, \
                                                        -148.3763630684420320 65.0137021238526813, \
                                                        -148.3768917281725237 65.0149357815308804, \
                                                        -148.3783168455451857 65.0151839028908967, \
                                                        -148.3814351427220117 65.0143437310382524, \
                                                        -148.3830196105515711 65.0149586418621652, \
                                                        -148.3849148151772397 65.0148263466171557, \
                                                        -148.3854207822145099 65.0157772774622913, \
                                                        -148.3877584164319785 65.0170117274922745, \
                                                        -148.3959299993289562 65.0200699997649849  ))")
#         expected_unwrapped = expected_wrapped

#         wkt = test_file.parse_geojson(file)
#         try:
#             actual_wrapped = shapely.wkt.loads(wkt["wkt"]["wrapped"])
#             actual_unwrapped = shapely.wkt.loads(wkt["wkt"]["unwrapped"])
#         except KeyError:
#             # This means the parse function failed to load the file:
#             print("OUTPUT: " + str(wkt))
#             assert False

#         assert expected_wrapped == actual_wrapped
#         assert expected_unwrapped == actual_unwrapped

#         # At time of writing this test, the rest of the repair message is: "... from 555 points to 233 points'"
#         assert "'Simplified shape from" in str(wkt["repairs"]) 
#         assert len(wkt["repairs"]) == 1


    ## This test fails because the "polygon" only has two points, and throws an error when
    ## parsed inside repairWKT. Should repairWKT handle this case, or should it be fixed
    ## inside parse_geojson? (Ideal fix be converting to line and continuing w/ warning? 
    ##   Or continuing wtih whatever convex_hulling the points returns?)
    # def test_featureCollectionGeometryCollection_1(self):
    #     file_path = os.path.join(self.resources_root, "featureCollectionGeometryCollection_1.geojson")
    #     file = open(file_path, "r")
    #     wkt = test_file.parse_geojson(file)
    #     print(wkt)

    # TODO: add test for single geom with "MultiPolygon" type. Currently gets passed into repairWKT.
    # Should maybe covert to multipoint and call convex_hull? Fix in parse_geojson or repairWKT? 

    # TODO: add test for geojson NOT containing geometry tag, just type/coords
    # ie. is this a valid geojson?:
    # {
    #     "type": "MultiPolygon", 
    #     "coordinates": [
    #         [
    #             [[40, 40], [20, 45], [45, 30], [40, 40]]
    #         ], 
    #         [
    #             [[20, 35], [10, 30], [10, 10], [30, 5], [45, 20], [20, 35]], 
    #             [[30, 20], [20, 15], [20, 25], [30, 20]]
    #         ]
    #     ]
    # }
    # easyist fix, wrap everything in { "geometry": file.read() }. Method already handles if
    # geom has no "coordinates" field, and skips over it
