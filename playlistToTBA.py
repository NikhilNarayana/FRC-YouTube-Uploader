#!/usr/bin/env python3
""" this script will take any playlist that uploaded videos using the uploader and link the matches to TBA"""

import simplejson as json
import youtubeup
from youtubeAuthenticate import *
from youtubeup import post_video, quarters_match_code, semis_match_code, finals_match_code, tiebreak_mnum

if __name__ == "__main__":
    PID = input("Playlist ID (starts with PL): ")
    TBAID = input("TBA ID: ")
    TBASECRET = input("TBA Secret: ")
    ecode = input("Event Code (eg: 2018incmp): ")

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
    nextPageToken = playlistitems_list["nextPageToken"]
    while ('nextPageToken' in playlistitems_list):
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
                mnum = "qm{}".format(
                    title[title.find("Match") + 5:].split(" ")[1])
            except IndexError as e:
                print(title)
                print(e)
            body = json.dumps({mnum: video_id})
            print("Posting {}".format(mnum))
            post_video(TBAID, TBASECRET, body, ecode, "match_videos")
        elif "Quarterfinal" in title:
            num = int(title[title.find("Match") + 5:].split(" ")[1])
            if "Tiebreak" in title:
                num = tiebreak_mnum(num, "qf")
            mnum = quarters_match_code("qf", num)
            body = json.dumps({mnum: video_id})
            print("Posting {}".format(mnum))
            post_video(TBAID, TBASECRET, body, ecode, "match_videos")
        elif "Semifinal" in title:
            num = int(title[title.find("Match") + 5:].split(" ")[1])
            if "Tiebreak" in title:
                num = tiebreak_mnum(num, "sf")
            mnum = semis_match_code("sf", num)
            body = json.dumps({mnum: video_id})
            print("Posting {}".format(mnum))
            post_video(TBAID, TBASECRET, body, ecode, "match_videos")
        elif "Final" in title:
            num = int(title[title.find("Match") + 5:].split(" ")[1])
            if "Tiebreak" in title:
                num = tiebreak_mnum(num, "f1m")
            mnum = finals_match_code("f1m", num)
            body = json.dumps({mnum: video_id})
            print("Posting {}".format(mnum))
            post_video(TBAID, TBASECRET, body, ecode, "match_videos")
        elif any(k in title for k in ("Opening", "Closing", "Awards", "Alliance", "Highlight")):
            body = json.dumps([video_id])
            print("Posting {}".format(title))
            post_video(TBAID, TBASECRET, body, ecode, "media")
        else:
            print("I don't know what this is")
            print(title)
            print(video_id)
