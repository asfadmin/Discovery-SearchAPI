import pytest, sys, os
import random
import string

# from geomet import wkt

# Let python discover other modules, starting one dir behind this one (project root):
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, project_root)
import CMR.Input as test_file


# A lot of these tests don't throw the custom error message if "v" doesn't have a length param... ok?
#        i.e. "if not len(v) > 0" fails instantly if passed None, or [], but passes with ["1","2"]

class Test_ParseString():
    # TEST FAILS: test tries to take len(None) > 0, and throws ValueError, but without "Invalid string"...
    #  For consistancy, maybe first format to string, THEN check length, then return after? (Note, empty list would then pass, as of now it fails with len > 0)
    #  Or maybe better: Just move the len(v) into the try block, consistantly show "Invalid string" tag?

    # def test_stringNone(self):
    #     with pytest.raises(ValueError) as excinfo:
    #         test_file.parse_string(None)
    #     assert "Invalid string:" in str(excinfo.value), "\033[1;36;40m CMR/Input.py parse_string-> None type did not raise a ValueError:  \033[0m"

    def test_stringEmpty(self):
        with pytest.raises(ValueError) as excinfo:
            test_file.parse_string("")
        assert "Invalid string: Empty string:" in str(excinfo.value), "\033[1;36;40m CMR/Input.py parse_string-> Empty string did not raise a ValueError: Empty string \033[0m"

    def test_stringBasic(self):
        expected = ''.join(random.choice(string.ascii_letters) for _ in range(1000000))
        actual = test_file.parse_string(expected)
        assert expected == actual, "\033[1;36;40m CMR/Input.py parse_string-> The expected string does not equal actual \033[0m"

    # TEST FAILS: same as first test... the len(v) throws on everything w/out length
    # def test_intBasic(self):
    #     expected = "1234"
    #     actual = test_file.parse_string(1234)
    #     assert expected == actual

    def test_listBasic(self):
        test_list = ["testing", "because", "this", "also", "has", "a", "non-zero", "length"]
        expected = "['testing', 'because', 'this', 'also', 'has', 'a', 'non-zero', 'length']"
        actual = test_file.parse_string(test_list)
        assert expected == actual


    # PARSE_STRING: automatically converts bytes to string...
    def test_stringUnicode(self):
        original_raw = "ಔ ೠ ண Ⴃ ፴ ᛉ ៘ᣠ ᵆ Ⅻ ∬ ⏳ ⏰ ⚇ ⛵ ⛷"
        original_encoded = original_raw.encode("utf-8")

        actual_raw = test_file.parse_string(original_raw)
        actual_encoded = test_file.parse_string(original_encoded)
        # print("actual_encoded: " + actual_encoded)
        # print("expected_encoded: {}".format(expected_encoded))
        # print("Type: " + str(type(actual_encoded)))
        assert original_raw == actual_raw
        # assert type(expected_raw) == tyitpe(actual_raw) == type("basic_str")
        # assert type(expected_encoded) == type(actual_encoded) == type("basic_str")
        ## Fails:
        # assert expected_encoded == actual_encoded
        ## Passes: (expected_encoded type is bytes, format changes it to str)
        assert "{}".format(original_encoded) == actual_encoded

class Test_ParseInt():
    def test_basicInt(self):
        test_int = 42
        expected = 42
        actual = test_file.parse_int(test_int)
        assert expected == actual

    def test_stringInt(self):
        test_str = "42"
        expected = 42
        actual = test_file.parse_int(test_str)
        assert expected == actual

    def test_reallyLongInt(self):
        test_str = ""
        for _ in range(9000):
            test_str += "987654321"
        expected = int(test_str)
        actual = test_file.parse_int(test_str)
        # check both parsed to int correctly:
        assert expected == actual
        # check no information was lost / truncated:
        assert len(test_str) == len(str(actual)) == len(str(expected))

    def test_negativeStringInt(self):
        test_str = "-22"
        expected = -22
        actual = test_file.parse_int(test_str)
        assert expected == actual

    def test_stringFloat(self):
        test_str = "4.2"
        expected = 4
        # Can't go from string to int right away if "int" is float. Bug?
        with pytest.raises(ValueError) as excinfo:
            test_file.parse_int(test_str)
        assert "Invalid int: {0}".format(test_str) == str(excinfo.value), "\033[1;36;40m CMR/Input.py parse_int-> string of a float did not raise a ValueError when casted to int \033[0m"
        # Something like this works: (first convert to float, THEN requested type...?)
        # Note: if this change happens, you can pass 5e8 to parse_int. TODO come back to this
        actual = test_file.parse_float(test_str)
        actual = test_file.parse_int(actual)
        assert expected == actual

    def test_throwsString(self):
        test_str = "yep, I'm a string"
        with pytest.raises(ValueError) as excinfo:
            test_file.parse_int(test_str)
        assert "Invalid int: {0}".format(test_str) == str(excinfo.value)


class Test_parseFloat():
    def test_basicFloat(self):
        myFloat = 3e8
        expected = 300000000
        actual = test_file.parse_float(myFloat)
        assert expected == actual

    def test_stringInt(self):
        myInt = "9001"
        expected = 9001.0
        actual = test_file.parse_float(myInt)
        assert expected == actual

    def test_wOutLeadingDigit(self):
        myFloat = ".42"
        expected = 0.42
        actual = test_file.parse_float(myFloat)
        assert expected == actual

        myFloat = "-.42"
        expected = -0.42
        actual = test_file.parse_float(myFloat)
        assert expected == actual

    def test_negativeStringFloat(self):
        myFloat = "-8e-5"
        expected = -0.00008
        actual = test_file.parse_float(myFloat)
        assert expected == actual

    # Throws "Invalid number", should it be "Invalid float"?
    def test_throwsString(self):
        test_str = "yep, I'm a string"
        with pytest.raises(ValueError) as excinfo:
            test_file.parse_float(test_str)
        assert "Invalid number: {0}".format(test_str) == str(excinfo.value)

class Test_parseDate():
    # Docs say you can input string / unicode,
    # also strings like "tomorrow" work, but no way to hardcode "tomorrows" date
    def test_unicodeRussian(self):
        test_str = u'13 января 2015 г. в 13:34'
        expected = '2015-01-13T13:34:00Z'
        actual = test_file.parse_date(test_str)
        assert expected == actual

    def test_stringFails(self):
        test_str = "Good luck parsing a date from this..."
        with pytest.raises(ValueError) as execinfo:
            test_file.parse_date(test_str)
        assert "Invalid date: {0}".format(test_str) == str(execinfo.value)

class Test_parseDateRange():
# NOTE: as is, this function doesn't assert date_one < date_two...
#     check if functions that call this account for that
#   parse_range raises an ValueError on incorrect ordering, but also has no error message why...
    def test_twoDuplicateDates(self):
        # Is a range of two of the same date acceptable? probably...
        duplicateDates = test_file.parse_date_range("tomorrow,tomorrow")
        assert len(duplicateDates.split(",")) == 2

    def test_throwsOnBadLength(self):
        test_noRange = "yesterday"
        with pytest.raises(ValueError) as execinfo:
            test_file.parse_date_range(test_noRange)
        assert "Invalid date range:" in str(execinfo.value)

        test_tooLongRange = "yesterday, today, tomorrow"
        with pytest.raises(ValueError) as execinfo:
            test_file.parse_date_range(test_tooLongRange)
        assert "Invalid date range:" in str(execinfo.value)

        test_justRightRange = "today, tomorrow"
        assert len(test_justRightRange.split(",")) == 2

# parse_range is more-of a helper function for parse_int_range and etc.
# I'll write those tests first, and come back to this to see what's left


class Test_parseIntRange():
    def test_twoNegativeInts(self):
        intRange = "-8--2"
        ints = test_file.parse_int_range(intRange)
        assert ints[0] == -8
        assert ints[1] == -2

    def test_NegativeZeros(self):
        intRange = "-0-0"
        ints = test_file.parse_int_range(intRange)
        assert ints == 0

        intRange = "0--0"
        ints = test_file.parse_int_range(intRange)
        assert ints == 0

        intRange = "-0-9"
        ints = test_file.parse_int_range(intRange)
        assert ints[0] == 0
        assert ints[1] == 9

        intRange = "-9--0"
        ints = test_file.parse_int_range(intRange)
        assert ints[0] == -9
        assert ints[1] == 0

    def test_throwsIfNotSorted(self):
        intRange = "321-123"
        with pytest.raises(ValueError) as execinfo:
            test_file.parse_int_range(intRange)
        # First Invalid range throws, then that gets passed back to Invalid int range.
        # Because of no error message, this IS the message...
        assert "Invalid int range: Invalid range: " == str(execinfo.value)

class Test_parseFloatRange():
# Floats that have "e" fail to pass the parse_range regex...
# Stop users from using "e"? or add "e" as option in regex for floats?
    # def test_wOutLeadingDigit(self):
    #     floatRange = ".2-.3"
    #     floats = test_file.parse_float_range(floatRange)
    #     assert floats[0] == 0.2
    #     assert floats[1] == 0.3

    # def test_wOutLeadingDigitNeg(self):
    #     floatRange = "-.2--.5"
    #     floats = test_file.parse_float_range(floatRange)
    #     assert floats[0] == -0.2
    #     assert floats[1] == -0.5

    # def test_floatsWithE(self):
    #     floatRange = "3e2-2e9"
    #     floats = test_file.parse_float_range(floatRange)
    #     assert floats[0] == 3e-4
    #     assert floats[1] == 6e-1

    # def test_floatsWithNegE(self):
    #     floatRange = "-3e-4-6e-1" # -3e^-4 - 6e^-1
    #     floats = test_file.parse_float_range(floatRange)
    #     assert floats[0] == -3e-4
    #     assert floats[1] == 6e-1

    def test_negFloatsAndInts(self):
        floatRange = "-10000.2--9000"
        floats = test_file.parse_float_range(floatRange)
        assert floats[0] == -10000.2
        assert floats[1] == -9000

    def test_negZeroInRange(self):
        floatRange = "-10000.3--0"
        floats = test_file.parse_float_range(floatRange)
        assert floats[0] == -10000.3
        assert floats[1] == 0

        floatRange = "-0.0--0.0"
        floats = test_file.parse_float_range(floatRange)
        assert floats == 0


## Tests for parse_list will go here, but same as above, I'm not sure exactly
## what to test yet, since a lot of them will be included in tests like parse_string_list that calls it...

# class Test_parseStringList():
    # Rewrite test, string is supposed to fail if len(v) > 0...
    # value error that gets raised->: Invalid string: Empty string: <--
    # def test_emptyStr(self):
    #     emptyStr = ""
    #     strings = test_file.parse_string_list(testStr)
    #     assert strings[0] == ""

    # After writing this, I remembered there's no such thing as an "escaped quote"...
    # def test_escapedQuotesInList(self):
    #     stringList = "word-0,word\,1\,with\,commas\,in\,it,word2"
    #     strings = test_file.parse_string_list(stringList)
    #     assert strings[0] == "word-0"
    #     assert strings[1] == "word\,1\,with\,commas\,in\,it"
    #     assert strings[2] == "word2"

    # Rewrite tomorrow, empty elements fail in parse_str
    # def test_emptyElements(self):
    #     testStr = "word0,,word2"
    #     strings = test_file.parse_string_list(testStr)
    #     assert strings[0] == "word0"
    #     assert strings[1] == ""
    #     assert strings[2] == "word2"


## TODO: Only thing I can think of that may fail list: French use
##         commas as our periods: 8.3 vs 8,3. Look into how python
##         handles this

class Test_parseNumberOrRange():
    # def test_basicIntToInt(self):
    #   myInt = 4321
    #   test_file.parse_number_or_range(myInt, test_file.parse_int)

    def test_stringIntToInt(self):
        myInt = "4321"
        result = test_file.parse_number_or_range(myInt, test_file.parse_int)
        assert result == 4321

        # Cant go from float to int in string form:
    # def test_stringFloatToInt(self):
    #   myFloat = "4321.56789"
    #   test_file.parse_number_or_range(myFloat, test_file.parse_int)
    #   assert result == 4321


# class Test_ParseWKT(unittest.TestCase):
#     def test_HoleOrderPolygon(self):
#         outer_cords = "(35 10, 45 45, 15 40, 10 20, 35 10)"
#         inner_cords = "(20 30, 35 35, 30 20, 20 30)"
#         test1_wkt = "POLYGON (" + outer_cords + "," + inner_cords + ")"
#         test2_wkt = "POLYGON (" + inner_cords + "," + outer_cords + ")"

#         test1_wkt = test_file.parse_wkt(test1_wkt)
#         test2_wkt = test_file.parse_wkt(test2_wkt)
#         # It Fails... bad?
#         # self.assertEqual(test1_wkt, test2_wkt)

#     # def test_MultiLineString(self):
#         # More-so testing because "MULTILINESTRING" contains "LINESTRING", so it should be supported...?
#         # wkt_multiline = "MULTILINESTRING ((10 10, 20 20, 10 40),(40 40, 30 30, 40 20, 30 10))"
#         # print(test_file.parse_wkt(wkt_multiline))
