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

if __name__ == '__main__':
	match_data = get_match_results("2016incmp","f1m1")
	for results in match_data['alliances']['blue']['teams']:
		print results[3:]