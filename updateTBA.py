#! /usr/bin/env python
"""This is a backup solution for if the main script doesn't update TBA properly"""

from youtubeup import post_video
from urlparse import *
import simplejson as json

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

vID = video_id(raw_input("Video Link: "))
link = raw_input("Blue Alliance Match Link (eg.https://www.thebluealliance.com/match/2017gaalb_sf1m1) : ")
codes = link.split("/")[-1].split("_")
request_body = json.dumps({codes[-1]: vID})
tbaID = raw_input("TBA ID: ")
tbaSecret = raw_input("TBA Secret: ")
post_video(tbaID, tbaSecret, request_body, codes[0], "match_video")