#!/usr/bin/python

import unittest
import tbaAPI
import youtubeAuthenticate
import TBA
import argparse
import youtubeup  as yup
import simplejson as json


class MyTests(unittest.TestCase):

    def test_get_hashtag(self):
        self.assertEqual(tbaAPI.get_hashtag("2016arc"), "arc")

    def test_parse_data(self):
    	blue_data = [132, "999", "180", "3166"]
    	red_data = [230, "5050", "1986", "1501"]
    	self.assertEqual(TBA.get_match_results("2016arc", "f1m1"), (blue_data, red_data))

    def test_create_title(self):
    	parser = argparse.ArgumentParser(description='argparse for testing')
    	args = parser.parse_args()
    	args.mcode = 1
    	args.mnum = 6
    	self.assertEqual(yup.quarters_yt_title(args), "2016 INFIRST Indiana State Championship - Quarterfinal Match 6")
    	self.assertNotEqual(yup.semis_yt_title(args), "2016 INFIRST Indiana State Championship - Quarterfinal Match 5")


if __name__ == '__main__':
    unittest.main()
