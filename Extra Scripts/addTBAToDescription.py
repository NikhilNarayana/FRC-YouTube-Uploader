#!/usr/bin/env python3

from .. import youtubeup as yup
from urllib.parse import *
from ..youtubeAuthenticate import *
from ..consts import *

data = """Red Alliance ({}, {}, {}) - {}
Blue Alliance ({}, {}, {}) - {}

"""
credits = """

Updated with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader)"""


def run(youtube, ID, ecode, mID, mnum, end):
    if end != 0:
        for vid in get_video_ids(youtube, ID):
            if int(mnum) <= int(end):
                update_description(youtube, vid, ecode, mID, mnum)
                mnum = int(mnum) + 1
    else:
        update_description(youtube, ID, ecode, mID, mnum)
    print("Updated all video descriptions")


# http://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
# Best way covering a variety of link styles
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


def get_video_ids(youtube, pID):
    playlistitems_list = youtube.playlistItems().list(
        playlistId=pID,
        part="snippet",
        maxResults=50
    ).execute()
    # Because of the YouTube API's pagination you need to grab every page with a token
    nextPageToken = playlistitems_list["nextPageToken"]
    while ('nextPageToken' in playlistitems_list):
        nextPageList = youtube.playlistItems().list(
            playlistId=pID,
            part="snippet",
            maxResults=50,
            pageToken=nextPageToken
        ).execute()
        playlistitems_list["items"] = playlistitems_list["items"] + nextPageList["items"]
        if "nextPageToken" not in nextPageList:
            playlistitems_list.pop('nextPageToken', None)
        else:
            nextPageToken = nextPageList['nextPageToken']
    for item in playlistitems_list["items"]:
        yield item["snippet"]["resourceId"]["videoId"]


def update_description(youtube, vID, ecode, mID, mnum):
    snippet = youtube.videos().list(
        part="snippet",
        id=vID).execute()
    olddesc = snippet['items'][0]['snippet']['description']
    mcode = yup.get_match_code(mID, int(mnum), "")
    blue_data, red_data = yup.get_match_results(ecode, mcode)
    newdesc = data.format(red_data[1], red_data[2], red_data[3], red_data[0], blue_data[1], blue_data[2], blue_data[3], blue_data[0]) + olddesc + credits
    snippet['items'][0]['snippet']['description'] = newdesc
    youtube.videos().update(
        part='snippet',
        body=dict(
            snippet=snippet['items'][0]['snippet'],
            id=vID)
    ).execute()
    print("Updated description of {}".format(vID))


if __name__ == "__main__":
    ECODE = input("Event Code: ")
    MCODE = input("Match Type (qm, qf, sf, or f1m)")
    MNUM = int(input("First Match Number: "))
    END = int(input("Last Match Number (0 if only updating one video): "))
    ID = None
    if not END:
        ID = video_id(input("Video link: "))
    else:
        ID = input("Playlist Link: ")
        f = ID.find("PL")
        ID = ID[f:f + 34]

    run(youtube, ID, ECODE, MCODE, MNUM, END)
