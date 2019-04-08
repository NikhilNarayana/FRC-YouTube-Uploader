#!/usr/bin/env python3
"""This is a backup solution for if the main script doesn't update TBA properly"""

import json
from urllib.parse import *

from . import consts


def video_id(value):
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return value


def main():
    loc = "match_video"
    request_body = None
    codes = None
    vID = video_id(input("Video Link: "))
    link = input("Blue Alliance Match Link (eg.https://www.thebluealliance.com/match/2017gaalb_sf1m1) : ")
    tbaID = input("TBA ID: ")
    tbaSecret = input("TBA Secret: ")
    codes = link.split("/")[-1].split("_")
    consts.tba.update_trusted(tbaID, tbaSecret, codes[0])
    if "media" in link:
        consts.tba.add_event_videos([vID])
    else:
        consts.tba.add_match_videos({codes[-1]: vID})
