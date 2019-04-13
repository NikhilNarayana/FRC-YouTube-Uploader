#!/usr/bin/env python3
""" this script will take any playlist that uploaded videos using the uploader and link the matches to TBA"""

import json
from .youtube import *
from . import consts
from .utils import quarters_match_code, semis_match_code, finals_match_code, tiebreak_mnum, get_match_results


def update_description(youtube, snippet, vID, ecode, mcode, ename, team, twit, fb, weblink):
    """
    Creates an updated TBA Description and updates the video
    """
    description = consts.DEFAULT_DESCRIPTION + consts.CREDITS
    print(snippet)
    blue_data, red_data = get_match_results(ecode, mcode)
    description = description.format(ecode=ecode, ename=ename, team=team, twit=twit, fb=fb, weblink=weblink, red1=red_data[1], red2=red_data[2], red3=red_data[3], redscore=red_data[0], blue1=blue_data[1], blue2=blue_data[2], blue3=blue_data[3], bluescore=blue_data[0])
    snippet['snippet']['description'] = description
    snippet['snippet']['categoryId'] = 28
    youtube.videos().update(
        part='snippet',
        body=dict(
            snippet=snippet['snippet'],
            id=vID)
    ).execute()
    print(f"Updated description of {vID}")


def main():
    PID = input("Link to Playlist: ")
    f = PID.find("PL")
    PID = PID[f:f + 34]
    TBAID = input("TBA ID: ")
    TBASECRET = input("TBA Secret: ")
    ecode = input("Event Code (eg: 2018incmp): ")
    ename = input("Event Name: ")
    team = input("Production Team Name: ")
    twit = input("Twitter Handle: ")
    fb = input("Facebook Name: ")
    weblink = input("Website Link")
    consts.tba.update_trusted(TBAID, TBASECRET, ecode)

    if (TBAID == "" or TBASECRET == ""):
        print("Can't add to TBA without ID and Secret")
        sys.exit(0)

    youtube = get_youtube_service()

    playlistitems_list = youtube.playlistItems().list(
        playlistId=PID,
        part="snippet",
        maxResults=50
    ).execute()

    print("got list")
    try:
        nextPageToken = playlistitems_list["nextPageToken"]
    except Exception as e:
        print(e)
    while ('nextPageToken' in playlistitems_list):
        nextPageToken = playlistitems_list["nextPageToken"]
        num = None
        print("getting next page")
        nextPageList = youtube.playlistItems().list(
            playlistId=PID,
            part="snippet",
            maxResults=50,
            pageToken=nextPageToken).execute()
        print("got next page")
        playlistitems_list["items"] = playlistitems_list["items"] + \
            nextPageList["items"]
        if "nextPageToken" not in nextPageList:
            playlistitems_list.pop('nextPageToken', None)
            print("no more pages")
        else:
            nextPageToken = nextPageList['nextPageToken']
            print("got next page token")
            # Print information about each video.

    for playlist_item in playlistitems_list["items"]:
        title = str(playlist_item["snippet"]["title"])
        video_id = str(playlist_item["snippet"]["resourceId"]["videoId"])
        if "Qual" in title:
            mnum = None
            try:
                mnum = f"qm{title[title.find('Match') + 5:].split(' ')[1]}"
            except IndexError as e:
                print(title)
                print(e)
            print(f"Posting {mnum}")
            consts.tba.add_match_videos({mnum: video_id})
            update_description(youtube, playlist_item, video_id, ecode, mnum, ename, team, twit, fb, weblink)
        elif "Quarterfinal" in title:
            try:
                num = int(title[title.find("Match") + 5:].split(" ")[1])
            except ValueError as e:
                num = int(title[title.find("Tiebreaker") + 10:].split(" ")[1])
            if "Tiebreak" in title:
                num = tiebreak_mnum(num, "qf")
            mnum = quarters_match_code("qf", num)
            print(f"Posting {mnum}")
            consts.tba.add_match_videos({mnum: video_id})
            update_description(youtube, playlist_item, video_id, ecode, mnum, ename, team, twit, fb, weblink)
        elif "Semifinal" in title:
            try:
                num = int(title[title.find("Match") + 5:].split(" ")[1])
            except ValueError as e:
                num = int(title[title.find("Tiebreaker") + 10:].split(" ")[1])
            if "Tiebreak" in title:
                num = tiebreak_mnum(num, "sf")
            mnum = semis_match_code("sf", num)
            print(f"Posting {mnum}")
            consts.tba.add_match_videos({mnum: video_id})
            update_description(youtube, playlist_item, video_id, ecode, mnum, ename, team, twit, fb, weblink)
        elif "Final" in title:
            try:
                num = int(title[title.find("Match") + 5:].split(" ")[1])
            except ValueError as e:
                num = int(title[title.find("Tiebreaker") + 10:].split(" ")[1])
            if "Tiebreak" in title:
                num = tiebreak_mnum(num, "f1m")
            mnum = finals_match_code("f1m", num)
            print(f"Posting {mnum}")
            consts.tba.add_match_videos({mnum: video_id})
            update_description(youtube, playlist_item, video_id, ecode, mnum, ename, team, twit, fb, weblink)
        elif any(k in title for k in ("Opening", "Closing", "Awards", "Alliance", "Highlight")):
            print(f"Posting {title}")
            consts.tba.add_event_videos([video_id])
        else:
            print("I don't know what this is")
            print(title)
            print(video_id)
