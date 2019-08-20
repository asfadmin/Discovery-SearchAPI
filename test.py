import unittest
from unittest import TestCase
import requests
import json

# Method from: https://stackoverflow.com/questions/21028979/recursive-iteration-through-nested-json-for-specific-key-in-python
def get_status(dict_var):
	for key, value in dict_var.items():
		if key == "ok?":
			print("HIT")
			yield value
		elif isinstance(value, dict):
			for id_val in get_status(value):
				yield id_val

class QuickTests(unittest.TestCase):
	def test_health(self):
		# https://stackoverflow.com/questions/25741188/saving-json-response-in-python
		url = "http://127.0.0.1:5000/health"
		response = requests.get(url)
		response = json.loads(response.content)
		self.assertTrue(response["ASFSearchAPI"]["ok?"] == True)
		self.assertTrue(response["CMRSearchAPI"]["health"]["echo"]["ok?"] == True)
		for stat in get_status(response):
			self.assertTrue(stat == True)

if __name__ == '__main__':
	unittest.main()