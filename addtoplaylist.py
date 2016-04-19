#!/usr/bin/python

import httplib2
import os
import sys

from apiclient.errors import HttpError
from oauth2client.tools import argparser
from youtubeAuthenticate import get_authenticated_service


#Default Variables
PLAYLIST_ID = "PL9UFVOe2UANx7WGnZG57BogYFKThwhIa2"
#How to get Playlist ID:
# Go to the creator studio -> Video Manager -> Playlists and pick the one you want to add to
# The playlist id will be listed in the URL https://www.youtube.com/playlist?list=PLXXXXXXXXXXXXXXXXXXXXXXX

def add_video_to_playlist(youtube,videoID,playlistID):
    add_video_request=youtube.playlistItems().insert(
    part="snippet",
    body={
        'snippet': {
            'playlistId': playlistID, 
            'resourceId': {
                    'kind': 'youtube#video',
                'videoId': videoID
            }
            #'position': 0
            }
    }
).execute()
    print "Added to playlist"

if __name__ == '__main__':
    argparser.add_argument("--vID",required=True,help="Video ID to add to playlist")
    args = argparser.parse_args()
    youtube = get_authenticated_service(args)
    add_video_to_playlist(youtube,args.vID,PLAYLIST_ID)