#!/usr/bin/python
import urllib2
from TheBlueAlliance import *
import requests

class Match(TheBlueAlliance.APIBase):
	EVENT_KEY = "YEARcode"
	def __init__(self, event_key):
		super(API, self).__init__("Nikhil Narayana","FRC Video Uploader","1.0")
		self.EVENT_KEY = event_key

urllib2.urlopen("http://www.thebluealliance.com/api/v2/match/2016incmp_f1m1").read()