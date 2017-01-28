#!/usr/bin/env python

import urllib2
import tbaAPI as tba
import requests
import simplejson as json


def get_event_type(event_key):
    event = tba.event_get(event_key)
    return event.info["event_type_string"]


def get_match_results(event_key, match_key):
    event = tba.event_get(event_key)
    match_data = event.get_match(match_key)
    if match_data is None:
        raise ValueError("""Match %s%s does not exist. Please use a match that exists""" % (event_key, match_key))
    blue_data, red_data = parse_data(match_data)
    return blue_data, red_data


def parse_data(match_data):
    if (tba.is_datafeed_down()):
        blue_data, red_data = [-1] * 4, [-1] * 4
        return blue_data, red_data
    else:
        blue = match_data['alliances']['blue']['teams']
        red = match_data['alliances']['red']['teams']
        blue1 = blue[0][3:]
        blue2 = blue[1][3:]
        blue3 = blue[2][3:]
        red1 = red[0][3:]
        red2 = red[1][3:]
        red3 = red[2][3:]
        blue_score = match_data['alliances']['blue']['score']
        red_score = match_data['alliances']['red']['score']
        blue_data = [blue_score, blue1, blue2, blue3]
        red_data = [red_score, red1, red2, red3]
        return blue_data, red_data


def post_video(token, secret, request_body, event_key):
    tba.post_video(token, secret, event_key, request_body)
    print "Successfully added to TBA"