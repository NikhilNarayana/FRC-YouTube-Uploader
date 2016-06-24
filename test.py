#!/usr/bin/python

import unittest
import tbaAPI
import youtubeAuthenticate
import TBA
import simplejson as json


class MyTests(unittest.TestCase):

    def test_get_hashtag(self):
        self.assertEqual(tbaAPI.get_hashtag("2016arc"), "arc")

    def test_parse_data(self):
    	blue_data = [132, "999", "180", "3166"]
    	red_data = [230, "5050", "1986", "1501"]
    	self.assertEqual(TBA.get_match_results("2016arc", "f1m1"), (blue_data, red_data))

if __name__ == '__main__':
    unittest.main()
