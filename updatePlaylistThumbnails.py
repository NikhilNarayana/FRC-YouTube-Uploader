#!/usr/bin/python

import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from updateThumbnail import update_thumbnail
from youtubeAuthenticate import get_authenticated_service

#Thumbnail file to use
THUMBNAIL = ""
PLAYLISTID = "PL9UFVOe2UANz-C62NqFLnebNieHc4Wiar"

# Retrieve the contentDetails part of the channel resource for the
# authenticated user's channel.
def update_thumbnails(youtube,pID):
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=PLAYLISTID,
        part="snippet",
        maxResults=50
    )

    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Print information about each video.
    for playlist_item in playlistitems_list_response["items"]:
        title = playlist_item["snippet"]["title"]
        video_id = playlist_item["snippet"]["resourceId"]["videoId"]
        update_thumbnail(youtube,video_id,THUMBNAIL)

    playlistitems_list_request = youtube.playlistItems().list_next(
        playlistitems_list_request, playlistitems_list_response)

if __name__ == '__main__':
    argparser.add_argument("--pID",help="PlaylistID of videos to change thumbnails for",default=PLAYLISTID)
    args = argparser.parse_args()
    youtube = get_authenticated_service(args)
