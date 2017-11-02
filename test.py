#!/usr/bin/env python

import unittest
import youtubeAuthenticate
import argparse
import youtubeup  as yup
import simplejson as json
import re
import tbapy
import nose


class MyTests(unittest.TestCase):
    def test_get_hashtag(self):
        self.assertEqual("frc" + re.search('\D+', "2016arc").group(), "frcarc")

    def test_parse_data(self):
        blue_data = [132, "999", "180", "3166"]
        red_data = [230, "5050", "1986", "1501"]
        self.assertEqual(yup.get_match_results("2016arc", "f1m1"), (blue_data, red_data))

    def test_create_title(self):
        parser = argparse.ArgumentParser(description='argparse for testing')
        args = parser.parse_args()
        args.mcode = 1
        args.mnum = 6
        args.ein = False
        args.ename = "2016 INFIRST Indiana State Championship"
        self.assertEqual(yup.quarters_yt_title(args), "2016 INFIRST Indiana State Championship - Quarterfinal Match 6")
        self.assertNotEqual(yup.semis_yt_title(args), "2016 INFIRST Indiana State Championship - Quarterfinal Match 5")

    def test_get_match_code(self):
        mcode = "qf"
        mnum = 5
        self.assertEqual(yup.quarters_match_code(mcode, mnum), ("qf1m2"))
        self.assertNotEqual(yup.semis_match_code(mcode, mnum), ("qf1m2"))

    def test_create_filename(self):
        parser = argparse.ArgumentParser(description='argparse for testing')
        args = parser.parse_args()
        args.mcode = 1
        args.mnum = 6
        args.ein = False
        args.ename = "2016 INFIRST Indiana State Championship"
        args.files = ("2016 INFIRST Indiana State Championship - Quarterfinal Match 6.mp4", "2016 INFIRST Indiana State Championship - Quarterfinal Match 3.mp4", "2016 INFIRST Indiana State Championship - Quarterfinal Match 1.mp4")
        self.assertEqual(yup.quarters_filename(args),
                         "2016 INFIRST Indiana State Championship - Quarterfinal Match 6.mp4")

    def test_tiebreaker_match_number(self):
        for x in range(1, 4):
            self.assertEqual(yup.tiebreak_mnum(x, "qf"), x + 8)
        for x in range(1, 2):
            self.assertEqual(yup.tiebreak_mnum(x, "sf"), x + 4)
        self.assertEqual(yup.tiebreak_mnum(3, "f1m"), 3)

    def test_description(self):
        parser = argparse.ArgumentParser(description='argparse for testing')
        args = parser.parse_args()
        args.ename, args.ecode, args.prodteam, args.twit, args.fb, args.weblink, args.mnum, args.mtype, args.mcode = "2016 Indiana State Championship", "2016incmp", "IndianaFIRST AV", "IndianaFIRST", "IndianaFIRST", "www.IndianaFIRST.org", 1, "qm", "qm1"
        args.ein = False
        blue_data, red_data, mcode = yup.tba_results(args)
        args.description = """Footage of the {} Event is courtesy of the {}.

Follow us on Twitter (@{}) and Facebook ({}).

For more information and future event schedules, visit our website: {}

Thanks for watching!

Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""
        expected_description = args.description.format(args.ename, args.prodteam, args.twit, args.fb, args.weblink)
        self.assertEqual(yup.create_description(args, -1, -1, -1, -1, -1, -1, -1, -1), expected_description)
        args.description = """Footage of the {} is courtesy of the {}.

Red Alliance  ({}, {}, {}) - {}
Blue Alliance ({}, {}, {}) - {}

To view match schedules and results for this event, visit The Blue Alliance Event Page: https://www.thebluealliance.com/event/{}

Follow us on Twitter (@{}) and Facebook ({}).

For more information and future event schedules, visit our website: {}

Thanks for watching!

Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""
        expected_description = args.description.format(str(args.ename), str(args.prodteam),
                str(red_data[1]), str(red_data[2]), str(red_data[3]), str(red_data[0]), str(blue_data[1]), str(blue_data[2]), str(blue_data[3]), str(blue_data[0]),
                str(args.ecode), str(args.twit), str(args.fb), str(args.weblink))
        self.assertEqual(yup.create_description(args, blue_data[1], blue_data[2], blue_data[3], blue_data[0],
                                                red_data[1], red_data[2], red_data[3], red_data[0]),
                         expected_description)
        args.description = "Haha"
        expected_description = "Haha"
        self.assertEqual(yup.create_description(args, blue_data[1], blue_data[2], blue_data[3], blue_data[0],
                                                red_data[1], red_data[2], red_data[3], red_data[0]),
                         expected_description)


if __name__ == '__main__':
    nose.main()
