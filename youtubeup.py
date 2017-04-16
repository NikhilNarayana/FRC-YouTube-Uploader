#!/usr/bin/python

import os
import sys
import time
import math
import random
import argparse
import datetime as dt

from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload

from tbaAPI import *
from youtubeAuthenticate import *

# Default Variables
DEFAULT_VIDEO_CATEGORY = 28
DEFAULT_THUMBNAIL = "thumbnail.png"
DEFAULT_TAGS = """{}, FIRST, omgrobots, FRC, FIRST Robotics Competition, robots, Robotics, FIRST STEAMworks"""
QUAL = "Qualification Match {}"
QUARTER = "Quarterfinal Match {}"
QUARTERT = "Quarterfinal Tiebreaker {}"
SEMI = "Semifinal Match {}"
SEMIT = "Semifinal Tiebreaker {}"
FINALS = "Final Match {}"
FINALST = "Final Tiebreaker"
EXTENSION = ".mp4"
MATCH_TYPE = ["qm", "qf", "sf", "f1m"]
DEFAULT_DESCRIPTION = """Footage of the {} is courtesy of the {}.

Red Alliance  ({}, {}, {}) - {}
Blue Alliance ({}, {}, {}) - {}

To view match schedules and results for this event, visit The Blue Alliance Event Page: https://www.thebluealliance.com/event/{}

Follow us on Twitter (@{}) and Facebook ({}).

For more information and future event schedules, visit our website: {}

Thanks for watching!

Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""

NO_TBA_DESCRIPTION = """Footage of the {} Event is courtesy of the {}.

Follow us on Twitter (@{}) and Facebook ({}).

For more information and future event schedules, visit our website: {}

Thanks for watching!

Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def quals_yt_title(options):
    return options.title.format(options.mnum)

def eights_yt_title(options):
    return None

def quarters_yt_title(options):
    mnum = options.mnum
    if 1 <= options.mnum <= 8:
        title = options.ename + " - " + QUARTER.format(mnum)
        return title
    elif 9 <= options.mnum <= 12:
        mnum -= 8
        title = options.ename + " - " + QUARTERT.format(mnum)
        return title
    else:
        raise ValueError("options.mnum must be within 1 and 12")

def semis_yt_title(options):
    mnum = options.mnum
    if 1 <= options.mnum <= 4:
        title = options.ename + " - " + SEMI.format(mnum)
        return title
    elif 5 <= options.mnum <= 6:
        mnum -= 4
        title = options.ename + " - " + SEMIT.format(mnum)
        return title
    else:
        raise ValueError("options.mnum must be within 1 and 6")

def finals_yt_title(options):
    title = options.ename + " - " + FINALS.format(options.mnum)
    return title

def ceremonies_title(options):
    title = None
    if options.ceremonies is 1 and not options.eday:
        title = options.ename + " - " + "{} Opening Ceremonies".format(options.day)
    else:
        title = options.ename + " - " + "Day {} Opening Ceremonies".format(options.eday)
    if options.ceremonies is 2:
        title = options.ename + " - " + "Alliance Selection"
    if options.ceremonies is 3 and not options.eday:
        title = options.ename + " - " + "Closing Ceremonies"
    else:
        title = options.ename + " - " + "Day {} Closing Ceremonies".format(options.eday)

def create_title(options):
    if options.ceremonies is 0:
        switcher = {
                "qm": quals_yt_title,
                "ef": eights_yt_title,
                "qf": quarters_yt_title,
                "sf": semis_yt_title,
                "f1m": finals_yt_title,
                }
        try:
            return switcher[options.mtype](options)
        except KeyError:
            print options.mtype
    else:
        return ceremonies_title(options)

def quals_filename(options):
    for f in options.files:
        fl = f.lower()
        if all(k in fl for k in ("qualification", " "+str(options.mnum)+".")):
            print "Found {} to upload".format(f)
            return f
    raise Exception("Cannot find Qualification file with match number {}".format(options.mnum))

def quarters_filename(options):
    if 1 <= options.mnum <= 8:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("quarter", "final", " "+str(options.mnum)+".")):
                if "tiebreak" not in fl:
                    print "Found {} to upload".format(f)
                    return f
    elif 9 <= options.mnum <= 12:
        mnum = options.mnum - 8
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("quarter", "tiebreak", "final"," "+str(mnum)+".")):
                print "Found {} to upload".format(f)
                return f

def semis_filename(options):
    if 1 <= options.mnum <= 4:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("semi", "final", " "+str(options.mnum)+".")):
                if "tiebreak" not in fl:
                    print "Found {} to upload".format(f)
                    return f
    elif 5 <= options.mnum <= 6:
        mnum = options.mnum - 4
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("semi", "tiebreak", "final"," "+str(mnum)+".")):
                print "Found {} to upload".format(f)
                return f

def finals_filename(options):
    if 1 <= options.mnum <= 2:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("final"," "+str(options.mnum)+".")):
                if all(k not in fl for k in ("quarter","semi")) and "tiebreak" not in fl:
                        print "Found {} to upload".format(f)
                        return f
    elif options.mnum >= 3:
        for f in options.files:
            fl = f.lower()
            if "final" in fl and any(k in fl for k in ("tiebreak", " "+str(options.mnum)+".")):
                if all(k not in fl for k in ("quarter","semi")):
                    print "Found {} to upload".format(f)
                    return f

def ceremonies_filename(options):
    if options.ceremonies is 1:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("opening", "ceremon")):
                if any(k in fl for k in (options.day.lower(), str(options.eday))):
                    print "Found {} to upload".format(f)
                    return f
    if options.ceremonies is 2:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("alliance", "selection")):
                print "Found {} to upload".format(f)
                return f
    if options.ceremonies is 3:
        for f in options.files:
            fl = f.lower()
            if any(k in fl for k in ("closing", "award")) and "ceremon" in fl:
                if any(k in fl for k in (options.day.lower(), str(options.eday))):
                    print "Found {} to upload".format(f)
                    return f

def create_filename(options):
    if options.ceremonies is 0:
        switcher = {
                "qm": quals_filename,
                "qf": quarters_filename,
                "sf": semis_filename,
                "f1m": finals_filename,
                }
        try:
            options.file = switcher[options.mtype](options)
            return options.file
        except KeyError:
            print options.mtype
    else:
        options.file = ceremonies_filename(options)
        return options.file
def quals_match_code(mcode, mnum):
    match_code = str(mcode) + str(mnum)
    return match_code

def eights_match_code(mcode, mnum):
    match_set = str(mnum % 8)
    match_code = None
    if match_set == "0":
        match_set = "8"
    if mnum <= 8:
        match_code = mcode + match_set + "m1"
    elif mnum <= 16:
        match_code = mcode + match_set + "m2"
    elif mnum <= 24:
        match_code = mcode + match_set + "m3"
    else:
        raise ValueError("Match Number can't be larger than 24")
    return match_code


def quarters_match_code(mcode, mnum):
    match_set = str(mnum % 4)
    match_code = None
    if match_set == "0":
        match_set = "4"
    if mnum <= 4:
        match_code = mcode + match_set + "m1"
    elif mnum <= 8:
        match_code = mcode + match_set + "m2"
    elif mnum <= 12:
        match_code = mcode + match_set + "m3"
    else:
        raise ValueError("Match Number can't be larger than 12")
    return match_code

def semis_match_code(mcode, mnum):
    match_set = str(mnum % 2)
    match_code = None
    if match_set == "0":
        match_set = "2"
    if mnum <= 2:
        match_code = mcode + match_set + "m1"
    elif mnum <= 4:
        match_code = mcode + match_set + "m2"
    elif mnum <= 6:
        match_code = mcode + match_set + "m3"
    else:
        raise ValueError("Match Number can't be larger than 6")
    return match_code

def finals_match_code(mcode, mnum):
    match_code = str(mcode) + str(mnum)
    return match_code

def get_match_code(mtype, mnum, mcode):
    if any(k == mcode for k in ("","0")):
        switcher = {
                "qm": quals_match_code,
                "ef": eights_match_code,
                "qf": quarters_match_code,
                "sf": semis_match_code,
                "f1m": finals_match_code,
        }
        return switcher[mtype](mtype, mnum)
    print "Uploading as {}".format(mcode)
    return mcode.lower()

def tba_results(options):
    mcode = get_match_code(options.mtype, options.mnum, options.mcode)
    blue_data, red_data = get_match_results(options.ecode, mcode)
    return blue_data, red_data, mcode

def create_description(options, blue1, blue2, blue3, blueScore, red1, red2, red3, redScore):
    if all(x <= -1 for x in (red1, red2, red3, redScore, blue1, blue2, blue3, blueScore)):
        return NO_TBA_DESCRIPTION.format(options.ename, options.prodteam, options.twit, options.fb, options.weblink)
    try:
        return options.description.format(str(options.ename), str(options.prodteam),
                str(red1), str(red2), str(red3), str(redScore), str(blue1), str(blue2), str(blue3), str(blueScore),
                str(options.ecode), str(options.twit), str(options.fb), str(options.weblink))
    except TypeError, e:
        print e
        return options.description

def tiebreak_mnum(mnum, mcode):
    switcher = {
            "qm": mnum,
            "ef": mnum + 16,
            "qf": mnum + 8,
            "sf": mnum + 4,
            "f1m": 3,
    }
    return switcher[mcode]

def upload_multiple_videos(youtube, spreadsheet, options):
    while options.mnum <= options.end:
        try:
            print initialize_upload(youtube, spreadsheet, options)
        except HttpError, e:
            print "An HTTP error {} occurred:\n{}\n".format(e.resp.status, e.content)
        options.then = dt.datetime.now()
        options.mnum = options.mnum + 1
    print "All matches have been uploaded"

def update_thumbnail(youtube, video_id, thumbnail):
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=thumbnail
        ).execute()
    print "Thumbnail added to video {}".format(video_id)

def add_to_playlist(youtube,videoID,playlistID):
    if type(videoID) is list: # Recursively add videos if videoID is list
        for vid in videoID:
            add_video_to_playlist(youtube,vid,playlistID)
    else:
        add_video_request=youtube.playlistItems().insert(
        part="snippet",
        body={
            'snippet': {
                'playlistId': playlistID, 
                'resourceId': {
                        'kind': 'youtube#video',
                    'videoId': videoID
                }
            }
        }
    ).execute()
        print "Added to playlist"

def init(options):
    """The program starts here"""
    options.day = dt.datetime.now().strftime("%A")
    options.files = list(reversed([f for f in os.listdir(options.where) 
        if os.path.isfile(os.path.join(options.where, f))]))
    options.tags = DEFAULT_TAGS.format(options.ecode)
    options.category = DEFAULT_VIDEO_CATEGORY
    options.title = options.ename + " - " + QUAL
    if any(k == options.description for k in ("Add alternate description here.","")):
        options.description = DEFAULT_DESCRIPTION
    #fix types
    options.ceremonies = int(options.ceremonies)
    options.tba = int(options.tba)
    options.mnum = int(options.mnum)
    options.tiebreak = int(options.tiebreak)
    options.eday = int(options.eday)

    if options.ceremonies != 0:
        options.tba = 0
    if options.tiebreak == 1:
        options.mnum = tiebreak_mnum(options.mnum, options.mtype)

    youtube = get_youtube_service()
    spreadsheet = get_spreadsheet_service()

    try:
        if int(options.end) > options.mnum:
            options.end = int(options.end)
            upload_multiple_videos(youtube, spreadsheet, options)
    except ValueError:
        try:
            print initialize_upload(youtube, spreadsheet, options)
        except HttpError, e:
            print "An HTTP error {} occurred:\n{}".format(e.resp.status, e.content)

def initialize_upload(youtube, spreadsheet, options):
    if not options.ceremonies:
        print "Initializing upload for {} match {}".format(options.mtype, options.mnum)
    else:
        print "Initializing upload for: {}".format(ceremonies_title(options))
    tags = None
    mcode = None
    if options.tba:
        blue_data, red_data, mcode = tba_results(options)
        tags = options.tags.split(",")
        tags.extend(["frc" + str(blue_data[1]), "frc" + str(blue_data[2]), "frc" + str(blue_data[3])])
        tags.extend(["frc" + str(red_data[1]), "frc" + str(red_data[2]), "frc" + str(red_data[3])])
        tags.append(get_event_hashtag(options.ecode))
        tags.extend(options.ename.split(" "))

        body = dict(
                snippet=dict(
                    title=create_title(options),
                    description=create_description(options, blue_data[1], blue_data[2], blue_data[3], blue_data[0],
                        red_data[1], red_data[2], red_data[3], red_data[0]),
                    tags=tags,
                    categoryId=options.category
                    ),
                status=dict(
                    privacyStatus=VALID_PRIVACY_STATUSES[0]
                    )
                )
    else:
        mcode = get_match_code(options.mtype, options.mnum, options.mcode)

        tags = options.tags.split(",")
        tags.append(get_event_hashtag(options.ecode))

        body = dict(
                snippet=dict(
                    title=create_title(options),
                    description=create_description(options, -1, -1, -1, -1, -1, -1, -1, -1),
                    tags=tags,
                    categoryId=options.category
                    ),
                status=dict(
                    privacyStatus=VALID_PRIVACY_STATUSES[0]
                    )
                )

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.where+create_filename(options),
            chunksize=-1, 
            resumable=True),
        )

    return resumable_upload(insert_request, options, mcode, youtube, spreadsheet)

def resumable_upload(insert_request, options, mcode, youtube, spreadsheet):
    response = None
    error = None
    sleep_minutes = 600
    retry = 0
    retryforlimit = 0
    retry_status_codes = get_retry_status_codes()
    retry_exceptions = get_retry_exceptions()
    max_retries = get_max_retries()
    print "Uploading {}".format(options.file)
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if 'id' in response:
                print "Video link is https://www.youtube.com/watch?v={}".format(response['id'])
                if any("thumbnail" in file for file in [f for f in os.listdir(".") if os.path.isfile(os.path.join(".", f))]):
                    update_thumbnail(youtube, response['id'], "thumbnail.png")
                else:
                    print "thumbnail.png does not exist"
                add_to_playlist(youtube, response['id'], options.pID)
                request_body = json.dumps({mcode: response['id']})
                if options.tba:
                    post_video(options.tbaID, options.tbaSecret, request_body, options.ecode)
                totalTime = dt.datetime.now() - options.then
                spreadsheetID = "18flsXvAcYvQximmeyG0-9lhYtb5jd_oRtKzIN7zQDqk"
                rowRange = "Data!A1:F1"
                wasBatch = "True" if any(options.end != y for y in ("Only for batch uploads", "")) else "False"
                usedTBA = "True" if options.tba == 1 else "False"
                values = [[str(dt.datetime.now()),str(totalTime),"https://www.youtube.com/watch?v={}".format(response['id']), usedTBA, options.ename, wasBatch]]
                body = {'values': values}
                appendSpreadsheet = spreadsheet.spreadsheets().values().append(spreadsheetId=spreadsheetID, range=rowRange, valueInputOption="USER_ENTERED", body=body).execute()
                return "DONE"
            else:
                exit("The upload failed with an unexpected response: {}".format(response))
        except HttpError, e:
            if e.resp.status in retry_status_codes:
                error = "A retriable HTTP error {} occurred:\n{}".format(e.resp.status,
                        e.content)
            elif "uploadLimitExceeded" in e.content:
                retryforlimit += 1
                if retryforlimit < max_retries:
                    print "Waiting {} minutes to avoid upload limit".format(sleep_minutes / 60)
                    for x in xrange(sleep_minutes):
                        time.sleep(1)
                        if x % 60 == 0:
                            print "Minute {} of {}".format(x/60, sleep_minutes/60)
                    sleep_minutes -= 60
                    error = None
                else:
                    print "Upload limit could not be avoided\n{} was not uploaded".format(options.file)
                    sys.exit(0)
            else:
                raise
        except retry_exceptions as e:
            error = "A retriable error occurred: {}".format(e)

        if error is not None:
            print error
            retry += 1
            if retry > max_retries:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print "Sleeping {} seconds and then retrying...".format(sleep_seconds)
            time.sleep(sleep_seconds)