#!/usr/bin/python

import unittest
import tbaAPI

class MyTests(unittest.TestCase):
	def test_yt_title(self):
		self.assertEqual(get_hashtag("2016arc"), "arc")

if __name__ == '__main__':
    unittest.main()