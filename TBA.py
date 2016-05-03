#!/usr/bin/python
import urllib2
import bluealliance as tba
import requests
import simplejson as json

def get_match_results(event_key, match_key):
	tba.set_api_key("Nikki-Narayana","FRC-Match-Uploader","1.0")
	event = tba.event_get(event_key)
	match_data = event.get_match(match_key)
	return match_data

def parse_data(match_data):
	blue = match_data['alliances']['blue']['teams']
	red = match_data['alliances']['red']['teams']
	blue1 = blue[0][3:]
	blue2 = blue[1][3:]
	blue3 = blue[2][3:]
	red1 = red[0][3:]
	red2 = red[1][3:]
	red3 = red[2][3:]
	print blue1, blue2, blue3
	print red1, red2, red3
	blue_score = match_data['alliances']['blue']['score']
	red_score = match_data['alliances']['red']['score']
	print blue_score, red_score
	return blue1, blue2, blue3, blue_score, red1, red2, red3, red_score

if __name__ == '__main__':
	match_data = get_match_results("2016incmp","f1m1")
	blue1, blue2, blue3, blue_score, red1, red2, red3, red_score = parse_data(match_data)
	print blue1, blue2, blue3, blue_score, red1, red2, red3, red_score