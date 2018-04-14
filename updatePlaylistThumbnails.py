#!/usr/bin/env python3

from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
from youtubeup import update_thumbnail
from youtubeAuthenticate import get_youtube_service

THUMBNAIL = ""
PLAYLISTID = ""
# Thumbnail file to use

# Retrieve the contentDetails part of the channel resource for the
# authenticated user's channel.


def update_thumbnails(youtube, pID, thumbnail):
    playlistitems_list = youtube.playlistItems().list(
        playlistId=pID,
        part="snippet",
        maxResults=50
    ).execute()
    nextPageToken = playlistitems_list["nextPageToken"]
    while ('nextPageToken' in playlistitems_list):
        print "getting next page"
        nextPageList = youtube.playlistItems().list(
            playlistId=pID,
            part="snippet",
            maxResults=50,
            pageToken=nextPageToken).execute()
        print "got next page"
        playlistitems_list["items"] = playlistitems_list["items"] + \
            nextPageList["items"]
        if "nextPageToken" not in nextPageList:
            playlistitems_list.pop('nextPageToken', None)
            print "no more pages"
        else:
            nextPageToken = nextPageList['nextPageToken']
            print "got next page token"
            # Print information about each video.
    errorvids = []
    for playlist_item in playlistitems_list["items"]:
        title = playlist_item["snippet"]["title"]
        video_id = playlist_item["snippet"]["resourceId"]["videoId"]
        try:
        	update_thumbnail(youtube, video_id, thumbnail)
        except HttpError as e:
            x = (title, video_id)
            errorvids.append(x)
        	continue
        print("thumbnail updated")

    for tup in errorvids:
        print(tup)


if __name__ == '__main__':
    youtube = get_youtube_service()
    try:
        update_thumbnails(youtube, PLAYLISTID, THUMBNAIL)
    except HttpError, e:
        print "An HTTP error {} occurred:\n{}".format(e.resp.status, e.content)
