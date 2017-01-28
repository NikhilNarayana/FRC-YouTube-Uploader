#!/usr/bin/env python

from apiclient.errors import HttpError
from oauth2client.tools import argparser
from updateThumbnail import update_thumbnail
from youtubeAuthenticate import get_youtube_service

# Thumbnail file to use
THUMBNAIL = ""
PLAYLISTID = ""


# Retrieve the contentDetails part of the channel resource for the
# authenticated user's channel.
def update_thumbnails(youtube, pID, thumbnail):
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=pID,
        part="snippet",
        maxResults=50
    )

    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

    # Print information about each video.
    for playlist_item in playlistitems_list_response["items"]:
        title = playlist_item["snippet"]["title"]
        video_id = playlist_item["snippet"]["resourceId"]["videoId"]
        update_thumbnail(youtube, video_id, thumbnail)

    playlistitems_list_request = youtube.playlistItems().list_next(
        playlistitems_list_request, playlistitems_list_response)


if __name__ == '__main__':
    argparser.add_argument("--pID", help="PlaylistID of videos to change thumbnails for", default=PLAYLISTID)
    argparser.add_argument("--tnail", help="Thumbnail filename, with extension, for playlist", default=THUMBNAIL)
    args = argparser.parse_args()
    youtube = get_youtube_service()
    try:
        update_thumbnails(youtube, args.pID, args, thumbnail)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
