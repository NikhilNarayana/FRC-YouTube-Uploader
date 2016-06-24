#!/usr/bin/python

import unittest
import tbaAPI
import youtubeAuthenticate

class MyTests(unittest.TestCase):
	def test_get_hashtag(self):
		self.assertEqual(tbaAPI.get_hashtag("2016arc"), "arc")
if __name__ == '__main__':
    unittest.main()