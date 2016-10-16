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
		self.assertEqual(tbaAPI.get_event_hashtag("2016arc"), "frcarc")

	def test_parse_data(self):
		blue_data = [132, "999", "180", "3166"]
		red_data = [230, "5050", "1986", "1501"]
		self.assertEqual(TBA.get_match_results("2016arc", "f1m1"), (blue_data, red_data))

	def test_create_title(self):
		parser = argparse.ArgumentParser(description='argparse for testing')
		args = parser.parse_args()
		args.mcode = 1
		args.mnum = 6
		args.ename = "2016 INFIRST Indiana State Championship"
		self.assertEqual(yup.quarters_yt_title(args), "2016 INFIRST Indiana State Championship - Quarterfinal Match 6")
		self.assertNotEqual(yup.semis_yt_title(args), "2016 INFIRST Indiana State Championship - Quarterfinal Match 5")
		self.assertRaises(ValueError, yup.finals_yt_title, args)

	def test_get_match_code(self):
		mcode = "qf"
		mnum = 5
		self.assertEqual(yup.quarters_match_code(mcode, mnum), ("qf1m2"))
		self.assertNotEqual(yup.semis_match_code(mcode, mnum), ("qf1m2"))
		self.assertRaises(ValueError, yup.finals_match_code, mcode, mnum)

	def test_create_filename(self):
		parser = argparse.ArgumentParser(description='argparse for testing')
		args = parser.parse_args()
		args.mcode = 1
		args.mnum = 6
		args.ename = "2016 INFIRST Indiana State Championship"
		self.assertEqual(yup.quarters_filename(args), "2016 INFIRST Indiana State Championship - Quarterfinal Match 6.mp4")
		self.assertNotEqual(yup.semis_filename(args), "2016 INFIRST Indiana State Championship - Quarterfinal Match 5.mp4")
		self.assertRaises(ValueError, yup.finals_filename, args)

	def test_tiebreaker_match_number(self):
		for x in range(1, 4):
			self.assertEqual(yup.tiebreak_mnum(x, "qf"), x+8)
		for x in range(1, 2):
			self.assertEqual(yup.tiebreak_mnum(x, "sf"), x+4)
		self.assertEqual(yup.tiebreak_mnum(3, "f1m"), 3)

if __name__ == '__main__':
	unittest.main()
