#!/usr/bin/python

import httplib
import httplib2
import os
import random
import sys
import time
import pyperclip
import urllib
import datetime

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from TheBlueAlliance import *
from addtoplaylist import add_video_to_playlist
from updateThumbnail import update_thumbnail
from youtubeAuthenticate import get_authenticated_service

NOW = datetime.datetime.now()

#Default Variables - A lot needs to be changed based on event
DEFAULT_DESCRIPTION = """Footage of the 2016 IndianaFIRST FRC District Championship Event is courtesy the IndianaFIRST AV Crew.

Blue Alliance (%d, %d, %d) - %d
Red Alliance  (%d, %d, %d) - %d

To view match schedules and results for this event, visit The Blue Alliance Event Page: https://www.thebluealliance.com/event/2016incmp 

Follow us on Twitter (@IndianaFIRST) and Facebook (IndianaFIRST). 

For more information and future event schedules, visit our website: www.indianafirst.org 

Thanks for watching!"""

DEFAULT_VIDEO_CATEGORY = 28
DEFAULT_THUMBNAIL = "thumbnail.png"
DEFAULT_PLAYLIST_ID = "PL9UFVOe2UANx7WGnZG57BogYFKThwhIa2"
DEFAULT_TAGS = "2016incmp, FIRST, omgrobots, FRC, FIRST Robotics Competition, automation, robots, Robotics, FIRST Stronghold, INFIRST, IndianaFIRST, Indiana, District Championship"
YEAR = str(NOW.year)
ORGANIZATION = "INFIRST"
EVENT_NAME = "Indiana State Championship"
QUAL = "Qualification Match %s"
QUARTER = "Quarterfinal Match %s"
QUARTERT = "Quarterfinal Tiebreaker %s"
SEMI = "Semifinal Match %s"
SEMIT = "Semifinal Tiebreaker %s"
FINALS = "Finals Match %s"
FINALST = "Finals Tiebreaker"
EXTENSION = ".mp4"
DEFAULT_TITLE = YEAR + " " + ORGANIZATION + " " + EVENT_NAME + " - " + QUAL #CHANGE BASED ON EVENT
DEFAULT_FILE = YEAR + " " + ORGANIZATION + " " + EVENT_NAME + " - " + QUAL + EXTENSION #CHANGE BASED ON EVENT
MATCH_CODES = ["qm%d","qf%dm%d","sf%dm%d","f1m%d"]

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title % options.mnum,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file % options.mnum, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request, options.mnum, options.mcode, youtube)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request, mnum, mcode, youtube):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print "Uploading file..."
      status, response = insert_request.next_chunk()
      if 'id' in response:
        print "Video id '%s' was successfully uploaded." % response['id']
        print "Video link is https://www.youtube.com/watch?v=%s" % response['id']
        update_thumbnail(youtube, response['id'], "thumbnail.png")
        print "Video thumbnail added"
        add_video_to_playlist(youtube,response['id'],DEFAULT_PLAYLIST_ID)
        #os.system("python addtoplaylist.py --vID " + response['id']) #Use as backup to the previous line
        pyperclip.copy('https://www.youtube.com/watch?v=%s' % response['id'])
        spam = pyperclip.paste()
        print "YouTube link copied to clipboard for TheBlueAlliance"

      else:
        exit("The upload failed with an unexpected response: %s" % response)
    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print error
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print "Sleeping %f seconds and then retrying..." % sleep_seconds
      time.sleep(sleep_seconds)

if __name__ == '__main__':
  argparser.add_argument("--mnum", help="Match Number to add", required=True)
  argparser.add_argument("--mcode", help="Match code (qm,qf,sf,f) starting at 0 ->3", default=0)
  argparser.add_argument("--file", help="Video file to upload", default=DEFAULT_FILE)
  argparser.add_argument("--title", help="Video title", default=DEFAULT_TITLE)
  argparser.add_argument("--description", help="Video description", default=DEFAULT_DESCRIPTION)
  argparser.add_argument("--category", default=DEFAULT_VIDEO_CATEGORY,
    help="Numeric video category. " +
      "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
  argparser.add_argument("--keywords", help="Video keywords, comma separated",
    default=DEFAULT_TAGS)
  argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
    default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
  args = argparser.parse_args()

  youtube = get_authenticated_service(args)
  try:
    initialize_upload(youtube, args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)