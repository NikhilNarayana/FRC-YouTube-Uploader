#!/usr/bin/env python

from apiclient.errors import HttpError
from oauth2client.tools import argparser
from youtubeAuthenticate import get_youtube_service

# Default Variables
THUMBNAIL = ""

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def update_thumbnail(youtube, video_id, file):
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=file
    ).execute()
    print "Thumbnail added to video %s" % video_id


if __name__ == '__main__':
    argparser.add_argument("--vID", help="Video ID of video to edit", required=True)
    argparser.add_argument("--file", help="Thumbnail file to upload", default=THUMBNAIL)
    args = argparser.parse_args()

    youtube = get_youtube_service(args)

    try:
        update_thumbnail(youtube, args.vID, args.file)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
