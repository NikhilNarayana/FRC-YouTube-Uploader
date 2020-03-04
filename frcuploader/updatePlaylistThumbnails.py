#!/usr/bin/env python3

from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
from .youtube import get_youtube_service
from googleapiclient.http import MediaFileUpload

THUMBNAIL = ""
PLAYLISTID = ""


def update_thumbnail(youtube, video_id, thumbnail):
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=thumbnail).execute()
    print(f"Thumbnail added to video {video_id}")


def update_thumbnails(youtube, pID, thumbnail):
    playlistitems_list = youtube.playlistItems().list(
        playlistId=pID, part="snippet", maxResults=50).execute()
    print(playlistitems_list)
    try:
        nextPageToken = playlistitems_list["nextPageToken"]
    except KeyError:
        print("Only one page")
    while ('nextPageToken' in playlistitems_list):
        print("getting next page")
        nextPageList = youtube.playlistItems().list(
            playlistId=pID,
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
    errorvids = []
    for playlist_item in playlistitems_list["items"]:
        title = playlist_item["snippet"]["title"]
        video_id = playlist_item["snippet"]["resourceId"]["videoId"]
        try:
            update_thumbnail(youtube, video_id, thumbnail)
        except HttpError:
            x = (title, video_id)
            errorvids.append(x)
            continue
        print("thumbnail updated")

    for tup in errorvids:
        print(tup)


def main():
    youtube = get_youtube_service()
    PID = input("Playlist Link: ")
    THUMBNAIL = input("Thumbnail file name: ")
    f = PID.find("PL")
    PID = PID[f:f+34]
    try:
        update_thumbnails(youtube, PID, THUMBNAIL)
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
