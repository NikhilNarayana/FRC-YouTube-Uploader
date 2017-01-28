#!/usr/bin/env python

import unittest
from frcUploader import TBA, youtubeAuthenticate, tbaAPI
import argparse
from frcUploader import youtubeup  as yup
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
        args.ext = ".mp4"
        args.ename = "2016 INFIRST Indiana State Championship"
        self.assertEqual(yup.quarters_filename(args),
                         "2016 INFIRST Indiana State Championship - Quarterfinal Match 6.mp4")
        self.assertNotEqual(yup.semis_filename(args),
                            "2016 INFIRST Indiana State Championship - Quarterfinal Match 5.mp4")
        self.assertRaises(ValueError, yup.finals_filename, args)

    def test_tiebreaker_match_number(self):
        for x in range(1, 4):
            self.assertEqual(yup.tiebreak_mnum(x, "qf"), x + 8)
        for x in range(1, 2):
            self.assertEqual(yup.tiebreak_mnum(x, "sf"), x + 4)
        self.assertEqual(yup.tiebreak_mnum(3, "f1m"), 3)

    def test_description(self):
        parser = argparse.ArgumentParser(description='argparse for testing')
        args = parser.parse_args()
        args.ename, args.ecode, args.prodteam, args.twit, args.fb, args.weblink, args.mnum, args.mcode = "2016 Indiana State Championship", "2016incmp", "IndianaFIRST AV", "IndianaFIRST", "IndianaFIRST", "www.IndianaFIRST.org", 1, "qm"
        blue_data, red_data, mcode = yup.tba_results(args)
        args.ddescription = True
        args.description = """Footage of the %s Event is courtesy of the %s.

		Follow us on Twitter (@%s) and Facebook (%s).

		For more information and future event schedules, visit our website: %s

		Thanks for watching!"""
        expected_description = """Footage of the 2016 Indiana State Championship Event is courtesy of the IndianaFIRST AV.

		Follow us on Twitter (@IndianaFIRST) and Facebook (IndianaFIRST).

		For more information and future event schedules, visit our website: www.IndianaFIRST.org

		Thanks for watching!

		Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""
        self.assertEqual(yup.create_description(args, -1, -1, -1, -1, -1, -1, -1, -1), expected_description)
        args.description = """Footage of the %s %s Event is courtesy of the %s.

		Red Alliance (%s, %s, %s) - %s
		Blue Alliance (%s, %s, %s) - %s

		To view match schedules and results for this event, visit The Blue Alliance Event Page: https://www.thebluealliance.com/event/%s

		Follow us on Twitter (@%s) and Facebook (%s).

		For more information and future event schedules, visit our website: %s

		Thanks for watching!"""
        expected_description = """Footage of the 2016 Indiana State Championship District Championship Event is courtesy of the IndianaFIRST AV.

		Red Alliance (4580, 3559, 1720) - 83
		Blue Alliance (71, 1741, 234) - 138

		To view match schedules and results for this event, visit The Blue Alliance Event Page: https://www.thebluealliance.com/event/2016incmp

		Follow us on Twitter (@IndianaFIRST) and Facebook (IndianaFIRST).

		For more information and future event schedules, visit our website: www.IndianaFIRST.org

		Thanks for watching!

		Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""
        self.assertEqual(yup.create_description(args, blue_data[1], blue_data[2], blue_data[3], blue_data[0],
                                                red_data[1], red_data[2], red_data[3], red_data[0]),
                         expected_description)
        args.ddescription = False
        args.description = "Haha"
        expected_description = "Haha"
        self.assertEqual(yup.create_description(args, blue_data[1], blue_data[2], blue_data[3], blue_data[0],
                                                red_data[1], red_data[2], red_data[3], red_data[0]),
                         expected_description)


if __name__ == '__main__':
    unittest.main()
