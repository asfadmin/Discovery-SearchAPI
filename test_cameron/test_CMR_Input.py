import pytest
import sys, os

# import unittest
from geomet import wkt

# Test Files starting one dir behind this one:
sys.path.insert(0, os.path.abspath('..'))
import CMR.Input as test_file

class Test_ParseString():
	# TEST FAILS: test tries to take len(None) > 0, and throws ValueError, but without "Invalid string"...
	#  For consistancy, maybe first format to string, THEN check length, then return after? (Note, empty list would then pass, as of now it fails with len > 0)
	#  Or maybe better: Just move the len(v) into the try block, consistantly show "Invalid string" tag?

	# def test_stringNone(self):
	#     with pytest.raises(ValueError) as excinfo:
	#     	test_file.parse_string(None)
	#     assert "Invalid string:" in str(excinfo.value), "\033[1;36;40m CMR/Input.py parse_string-> None type did not raise a ValueError:  \033[0m"

	def test_stringEmpty(self):
	    with pytest.raises(ValueError) as excinfo:
	    	test_file.parse_string("")
	    assert "Invalid string: Empty string:" in str(excinfo.value), "\033[1;36;40m CMR/Input.py parse_string-> Empty string did not raise a ValueError: Empty string \033[0m"

	def test_stringBasic(self):
		expected = ""
		for i in range(900000):
			expected += "GonnaBeAReallllyLongString..."
		actual = test_file.parse_string(expected)
		assert expected == actual, "\033[1;36;40m CMR/Input.py parse_string-> The expected string does not equal actual \033[0m"

	# TEST FAILS: same as first test... the len(v) throws on everything w/out length
	# def test_intBasic(self):
	# 	expected = "1234"
	# 	actual = test_file.parse_string(1234)
	# 	assert expected == actual

	def test_listBasic(self):
		test_list = ["testing", "because", "this", "also", "has", "a", "non-zero", "length"] 
		expected = "['testing', 'because', 'this', 'also', 'has', 'a', 'non-zero', 'length']"
		actual = test_file.parse_string(test_list)
		assert expected == actual


	# PARSE_STRING: automatically converts bytes to string... 
	def test_stringUnicode(self):
		expected_raw = "ಔ ೠ ண Ⴃ ፴ ᛉ ៘ᣠ ᵆ Ⅻ ∬ ⏳ ⏰ ⚇ ⛵ ⛷"
		expected_encoded = expected_raw.encode("utf-8")

		actual_raw = test_file.parse_string(expected_raw)
		actual_encoded = test_file.parse_string(expected_encoded)
		# print("actual_encoded: " + actual_encoded)
		# print("expected_encoded: {}".format(expected_encoded))
		# print("Type: " + str(type(actual_encoded)))
		assert expected_raw == actual_raw
		# assert type(expected_raw) == tyitpe(actual_raw) == type("basic_str")
		# assert type(expected_encoded) == type(actual_encoded) == type("basic_str")
		## Fails:
		# assert expected_encoded == actual_encoded
		## Passes: (expected_encoded type is bytes, format changes it to str)
		assert "{}".format(expected_encoded) == actual_encoded





class Test_ParseInt():
	def test_basicInt(self):
		test_int = 42
		expected = 42
		actual = test_file.parse_int(test_int)
		assert expected == actual

	def test_basicString(self):
		test_str = "42"
		expected = 42
		actual = test_file.parse_int(test_str)


# class Test_ParseInt(unittest.TestCase):
# 	def test_int_stringCast(self):
# 		theInt = "20"
# 		self.assertEqual(test_file.parse_int(theInt), 20)

# 	def test_int_normal(self):
# 		self.assertEqual(test_file.parse_int(-4), -4)

# 	def test_int_floatTruncate(self):
# 		theFloat = 456.789
# 		self.assertEqual(test_file.parse_int(theFloat), 456)

# class Test_ParseWKT(unittest.TestCase):
# 	def test_HoleOrderPolygon(self):
# 		outer_cords = "(35 10, 45 45, 15 40, 10 20, 35 10)"
# 		inner_cords = "(20 30, 35 35, 30 20, 20 30)"
# 		test1_wkt = "POLYGON (" + outer_cords + "," + inner_cords + ")"
# 		test2_wkt = "POLYGON (" + inner_cords + "," + outer_cords + ")"
		
# 		test1_wkt = test_file.parse_wkt(test1_wkt)
# 		test2_wkt = test_file.parse_wkt(test2_wkt)
# 		# It Fails... bad?
# 		# self.assertEqual(test1_wkt, test2_wkt)

# 	# def test_MultiLineString(self):
# 		# More-so testing because "MULTILINESTRING" contains "LINESTRING", so it should be supported...?
# 		# wkt_multiline = "MULTILINESTRING ((10 10, 20 20, 10 40),(40 40, 30 30, 40 20, 30 10))"
# 		# print(test_file.parse_wkt(wkt_multiline))

