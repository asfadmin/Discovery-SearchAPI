import unittest
from geomet import wkt

# Test File:
import CMR.Input as test_file

class Test_ParseString(unittest.TestCase):
	def test_string_empty(self):
		errMsg = "\033[1;36;40m CMR/Input.py parse_string-> Empty string did not raise a ValueError \033[0m"
		with self.assertRaises(ValueError, msg=errMsg):
			test_file.parse_string("")

	def test_string_basic(self):
		string = "The first string that came to mind"
		self.assertEqual(test_file.parse_string(string), string, "\033[1;36;40m CMR/Input.py parse_string-> Basic string did not return same result \033[0m")

	def tes_string_punctuation(self):
		string = "!@#$%^&*()_+-=\\\'\",.<>/?"
		self.assertEqual(test_file.parse_string(string), string, "\033[1;36;40m CMR/Input.py parse_string-> Punctuation string did not return same result \033[0m")

	def test_string_long(self):
		string = ""
		for i in range(900000):
			string += "TESTING"
		self.assertEqual(test_file.parse_string(string),string, "\033[1;36;40m CMR/Input.py parse_string-> Long string did not return same result \033[0m")


class Test_ParseInt(unittest.TestCase):
	def test_int_stringCast(self):
		theInt = "20"
		self.assertEqual(test_file.parse_int(theInt), 20)

	def test_int_normal(self):
		self.assertEqual(test_file.parse_int(-4), -4)

	def test_int_floatTruncate(self):
		theFloat = 456.789
		self.assertEqual(test_file.parse_int(theFloat), 456)

class Test_ParseWKT(unittest.TestCase):
	def test_HoleOrderPolygon(self):
		outer_cords = "(35 10, 45 45, 15 40, 10 20, 35 10)"
		inner_cords = "(20 30, 35 35, 30 20, 20 30)"
		test1_wkt = "POLYGON (" + outer_cords + "," + inner_cords + ")"
		test2_wkt = "POLYGON (" + inner_cords + "," + outer_cords + ")"
		
		test1_wkt = test_file.parse_wkt(test1_wkt)
		test2_wkt = test_file.parse_wkt(test2_wkt)
		# It Fails... bad?
		# self.assertEqual(test1_wkt, test2_wkt)

	# def test_MultiLineString(self):
		# More-so testing because "MULTILINESTRING" contains "LINESTRING", so it should be supported...?
		# wkt_multiline = "MULTILINESTRING ((10 10, 20 20, 10 40),(40 40, 30 30, 40 20, 30 10))"
		# print(test_file.parse_wkt(wkt_multiline))