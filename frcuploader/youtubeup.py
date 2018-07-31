#!/usr/bin/env python3

import os
import re
import time
import errno
import random
import hashlib
import datetime as dt
from decimal import Decimal

import json
import requests
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from .consts import *

from cachecontrol import CacheControl
from cachecontrol.heuristics import ExpiresAfter

app_id = {'X-TBA-App-Id': ""}
trusted_auth = {'X-TBA-Auth-Id': "", 'X-TBA-Auth-Sig': ""}

s = requests.Session()
s = CacheControl(s, heuristic=ExpiresAfter(minutes=1))
s.headers.update(app_id)
"""Utility Functions"""


def convert_bytes(num):
    for x in sizes:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(path):
    file_info = os.stat(path)
    return convert_bytes(file_info.st_size)


"""YouTube Title Generators"""


def quals_yt_title(options):
    return options.title


def quarters_yt_title(options):
    mnum = options.mnum
    if mnum <= 8:
        return options.ename + f" - Quarterfinal Match {mnum}"
    elif mnum <= 12:
        mnum -= 8
        return options.ename + f" - Quarterfinal Tiebreaker {mnum}"
    else:
        raise ValueError("options.mnum must be within 1 and 12")


def semis_yt_title(options):
    mnum = options.mnum
    if mnum <= 4:
        return options.ename + f" - Semifinal Match {mnum}"
    elif mnum <= 6:
        mnum -= 4
        return options.ename + f" - Semifinal Tiebreaker {mnum}"
    else:
        raise ValueError("options.mnum must be within 1 and 6")


def finals_yt_title(options):
    return options.ename + f" - Final Match {options.mnum}"


def ceremonies_yt_title(options):
    title = None
    if options.ceremonies is 1:
        if not options.eday:
            title = f"{options.ename} - {options.day} Opening Ceremonies"
        else:
            title = f"{options.ename} - Day {options.eday} Opening Ceremonies"
    elif options.ceremonies is 2:
        title = f"{options.ename} - Alliance Selection"
    elif options.ceremonies is 3:
        if not options.eday:
            title = f"{options.ename} - Closing Ceremonies"
        else:
            title = f"{options.ename} - Day {options.eday} Closing Ceremonies"
    elif options.ceremonies is 4:
        title = f"{options.ename} - Highlight Reel"
    return title


"""File Location Functions"""


def quals_filename(options):
    file = None
    for f in options.files:
        fl = f.lower()
        if all([" " + str(options.mnum) + "." in fl and any(k in fl for k in ("qual", "qualification", "qm"))]):
            file = f
            break
    if file is None:
        print("No File Found")
    return file


def quarters_filename(options):
    file = None
    if 1 <= options.mnum <= 8:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("quarter", "final", " " + str(options.mnum) + ".")):
                if "tiebreak" not in fl:
                    file = f
                    break
    elif 9 <= options.mnum <= 12:
        mnum = options.mnum - 8
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("quarter", "tiebreak", "final", " " + str(mnum) + ".")):
                file = f
                break
    if file is None:
        print("No File Found")
    return file


def semis_filename(options):
    file = None
    if options.mnum <= 4:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("semi", "final", " " + str(options.mnum) + ".")):
                if "tiebreak" not in fl:
                    file = f
                    break
    elif options.mnum <= 6:
        mnum = options.mnum - 4
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("semi", "tiebreak", "final", " " + str(mnum) + ".")):
                file = f
                break
    if file is None:
        print("No File Found")
    return file


def finals_filename(options):
    file = None
    if options.mnum <= 2:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("final", " " + str(options.mnum) + ".")):
                if all(k not in fl for k in ("quarter", "semi")) and "tiebreak" not in fl:
                    file = f
                    break
    elif options.mnum >= 3:
        for f in options.files:
            fl = f.lower()
            if "final" in fl and any(k in fl for k in ("tiebreak", " " + str(options.mnum) + ".")):
                if all(k not in fl for k in ("quarter", "semi")):
                    file = f
                    break
    if file is None:
        print("No File Found")
    return file


def ceremonies_filename(options):
    file = None
    if options.ceremonies is 1:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("opening", "ceremon")):
                if any(k in fl for k in (options.day.lower(), f"day {options.eday}")):
                    file = f
                    break
    elif options.ceremonies is 2:
        for f in options.files:
            fl = f.lower()
            if all(k in fl for k in ("alliance", "selection")):
                file = f
                break
    elif options.ceremonies is 3:
        for f in options.files:
            fl = f.lower()
            if any(k in fl for k in ("closing", "award")) and "ceremon" in fl:
                if any(
                        k in fl for k in (options.day.lower(), f"day {options.eday}")):
                    file = f
                    break
                elif options.eday == 0:
                    file = f
                    break
    elif options.ceremonies is 4:
        for f in options.files:
            fl = f.lower()
            if any(k in fl for k in ("highlight", "wrapup", "recap")):
                file = f
                break
    if file is None:
        print("No File Found")
    return file


def create_names(options):
    if options.ceremonies is 0:
        fname = {
            "qm": quals_filename,
            "qf": quarters_filename,
            "sf": semis_filename,
            "f1m": finals_filename,
        }
        yt = {
            "qm": quals_yt_title,
            "qf": quarters_yt_title,
            "sf": semis_yt_title,
            "f1m": finals_yt_title,
        }
        try:
            return fname[options.mtype](options), yt[options.mtype](options)
        except KeyError:
            print(options.mtype)
    else:
        return ceremonies_filename(options), ceremonies_yt_title(options)


"""Match Code Generators"""


def quals_match_code(mtype, mnum):
    match_code = str(mtype) + str(mnum)
    return match_code


def quarters_match_code(mtype, mnum):
    match_set = str(mnum % 4)
    match_set = "4" if match_set == "0" else match_set
    match_code = mtype + match_set
    if mnum <= 4:
        match_code += "m1"
    elif mnum <= 8:
        match_code += "m2"
    elif mnum <= 12:
        match_code += "m3"
    else:
        raise ValueError("Match Number can't be larger than 12")
    return match_code


def semis_match_code(mtype, mnum):
    match_set = str(mnum % 2)
    match_set = "2" if match_set == "0" else match_set
    match_code = mtype + match_set
    if mnum <= 2:
        match_code += "m1"
    elif mnum <= 4:
        match_code += "m2"
    elif mnum <= 6:
        match_code += "m3"
    else:
        raise ValueError("Match Number can't be larger than 6")
    return match_code


def finals_match_code(mtype, mnum):
    match_code = mtype + str(mnum)
    return match_code


def get_match_code(mtype, mnum, mcode):
    if any(k == mcode for k in ("", "0")):
        switcher = {
            "qm": quals_match_code,
            "qf": quarters_match_code,
            "sf": semis_match_code,
            "f1m": finals_match_code,
        }
        return switcher[mtype](mtype, mnum)
    print(f"Uploading as {mcode}")
    return mcode.lower()


"""Data Compliation and Adjustment Functions"""


def get_match_results(event_key, match_key):
    match_data = tba.match("_".join([event_key, match_key]))
    if match_data is None:
        raise ValueError(f"{event_key} {match_key} does not exist on TBA. Please use a match that exists")
    blue_data, red_data = parse_data(match_data)
    while (blue_data[0] == -1 or red_data[0] == -1):
        print("Waiting 1 minute for TBA to update scores")
        time.sleep(60)
        match_data = tba.match("_".join([event_key, match_key]))
        blue_data, red_data = parse_data(match_data)
    return blue_data, red_data


def parse_data(match_data):
    blue = match_data['alliances']['blue']['team_keys']
    red = match_data['alliances']['red']['team_keys']
    blue_data = [match_data['alliances']['blue']['score']]
    red_data = [match_data['alliances']['red']['score']]
    for team in blue:
        blue_data.append(team[3:])
    for team in red:
        red_data.append(team[3:])
    return blue_data, red_data


def tba_results(options):
    mcode = get_match_code(options.mtype, options.mnum, options.mcode)
    blue_data, red_data = get_match_results(options.ecode, mcode)
    return blue_data, red_data, mcode


def create_description(options, blueScore, blue1, blue2, blue3, redScore, red1,
                       red2, red3):
    if all(x == -1 for x in (red1, red2, red3, redScore, blue1, blue2, blue3,
                             blueScore)):
        return NO_TBA_DESCRIPTION.format(
            ename=options.ename,
            team=options.prodteam,
            twit=options.twit,
            fb=options.fb,
            weblink=options.weblink)
    try:
        return options.description.format(
            ename=options.ename,
            team=options.prodteam,
            red1=red1,
            red2=red2,
            red3=red3,
            redscore=redScore,
            blue1=blue1,
            blue2=blue2,
            blue3=blue3,
            bluescore=blueScore,
            ecode=options.ecode,
            twit=options.twit,
            fb=options.fb,
            weblink=options.weblink)
    except TypeError as e:
        print(e)
        return options.description


def tiebreak_mnum(mnum, mtype):
    switcher = {
        "qm": mnum,
        "qf": mnum + 8,
        "sf": mnum + 4,
        "f1m": 3,
    }
    return switcher[mtype]


"""Additional YouTube Functions"""


def upload_multiple_videos(youtube, spreadsheet, options):
    while options.mnum <= options.end:
        try:
            while options.file is None and options.mnum < options.end:
                print(f"{options.mtype.upper()} Match {options.mnum} is missing")
                options.mnum = options.mnum + 1
                options.file, options.yttitle = create_names(options)
            if options.file is None:
                print("Can't upload")
            else:
                conclusion = initialize_upload(youtube, spreadsheet, options)
                if conclusion == "FAILED":
                    print("Try again")
                    return
                print(conclusion)
                options.then = dt.datetime.now()
                options.mnum = options.mnum + 1
                if options.mnum <= options.end:
                    options.file, options.yttitle = create_names(options)
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}\n")
    print("All matches have been uploaded")


def update_thumbnail(youtube, video_id, thumbnail):
    youtube.thumbnails().set(videoId=video_id, media_body=thumbnail).execute()
    print(f"Thumbnail added to video {video_id}")


def add_to_playlist(youtube, videoID, playlistID):
    if type(videoID) is list:  # Recursively add videos if videoID is list
        for vid in videoID:
            add_video_to_playlist(youtube, vid, playlistID)
    else:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                'snippet': {
                    'playlistId': playlistID,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': videoID
                    }
                }
            }).execute()
        print("Added to playlist")


def attempt_retry(error, retry, max_retries):
    if error is not None:
        print(error)
        retry += 1
        if retry > max_retries:
            exit("No longer attempting to retry.")

        max_sleep = 2**retry
        sleep_seconds = random.random() * max_sleep
        print(f"Sleeping {sleep_seconds} seconds and then retrying...")
        time.sleep(sleep_seconds)
        return None


"""TBA Trusted API"""


def post_video(token, secret, match_video, event_key, loc="match_videos"):
    trusted_auth = {'X-TBA-Auth-Id': "", 'X-TBA-Auth-Sig': ""}
    trusted_auth['X-TBA-Auth-Id'] = token
    request_path = f"/api/trusted/v1/event/{event_key}/{loc}/add"
    concat = secret + request_path + str(match_video)
    md5 = hashlib.md5(concat.encode("utf-8")).hexdigest()
    trusted_auth['X-TBA-Auth-Sig'] = str(md5)
    url_str = f"https://www.thebluealliance.com/api/trusted/v1/event/{event_key}/{loc}/add"
    if DEBUG:
        url_str = f"http://localhost:8080/api/trusted/v1/event/{event_key}/{loc}/add"
    if trusted_auth['X-TBA-Auth-Id'] == "" or trusted_auth['X-TBA-Auth-Sig'] == "":
        print("""TBA ID and/or TBA secret missing. Please set them in the UI""")
        return
    r = s.post(url_str, data=match_video, headers=trusted_auth)
    print(r.status_code)
    while 405 == r.status_code:
        print("Failed to POST to TBA")
        print("Attempting to POST to TBA again")
        r = s.post(url_str, data=match_video, headers=trusted_auth)
    if r.status_code > 299:
        print(r.text)
    elif "Success" in r.text or r.status_code == 200:
        print("Successfully added to TBA")
    else:
        print(r.text)
        print("Something went wrong")


def init(options):
    """The program starts here, options is a Namespace() object"""
    options.privacy = VALID_PRIVACY_STATUSES[0]  # privacy is always public
    if DEBUG:
        options.privacy = VALID_PRIVACY_STATUSES[
            1]  # set to unlisted if debugging
    options.day = dt.datetime.now().strftime(
        "%A")  # weekday in english ex: "Monday"
    options.files = list(
        reversed([
            f for f in os.listdir(options.where)
            if os.path.isfile(os.path.join(options.where, f))
        ]))
    options.tags = DEFAULT_TAGS.format(
        options.ecode, game=GAMES[
            options.ecode[:4]])  # add the ecode and game to default tags
    # default category is science & technology
    options.category = 28
    options.title = options.ename + f" - Qualification Match {options.mnum}"  # default title
    if any(k == options.description
           for k in ("Add alternate description here.", "",
                     DEFAULT_DESCRIPTION)):
        options.description = DEFAULT_DESCRIPTION + CREDITS
    else:
        options.description += CREDITS

    # fix types except options.end
    options.ceremonies = int(options.ceremonies)
    options.mnum = int(options.mnum)
    options.eday = int(options.eday)

    # seperate case to push to TBA
    if options.ceremonies != 0:
        if options.tba:
            options.post = True
        else:
            options.post = False
        options.tba = False
    if options.tiebreak:
        options.mnum = tiebreak_mnum(options.mnum, options.mtype)

    options.file, options.yttitle = create_names(options)

    if options.file is not None:
        print(f"Found {options.file} to upload")
        try:
            if int(options.end) > options.mnum:
                options.end = int(options.end)
                upload_multiple_videos(youtube, spreadsheet, options)
        except ValueError:
            try:
                print(initialize_upload(youtube, spreadsheet, options))
            except HttpError as e:
                print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
    else:
        print("First file must exist")
        print("Current settings:")
        print(f"Match Type: {options.mtype}")
        print(f"Match Number: {options.mnum}")
        print("Please check that a file matches the match type and number")


def initialize_upload(youtube, spreadsheet, options):
    if not options.ceremonies:
        print(f"Initializing upload for {options.mtype} match {options.mnum}")
    else:
        print(f"Initializing upload for: {ceremonies_yt_title(options)}")
    if options.tba:
        blue_data, red_data, mcode = tba_results(options)
        tags = options.tags.split(",")
        for team in blue_data[1:] + red_data[1:]:
            tags.append(f"frc{team}")
        tags.extend(options.ename.split(" "))
        tags.append("frc" + re.search('\D+', options.ecode).group())

        body = dict(
            snippet=dict(
                title=options.yttitle,
                description=create_description(options, *blue_data, *red_data),
                tags=tags,
                categoryId=options.category),
            status=dict(privacyStatus=options.privacy))
    else:
        mcode = get_match_code(options.mtype, options.mnum, options.mcode)

        tags = options.tags.split(",")
        tags.append("frc" + re.search('\D+', options.ecode).group())

        body = dict(
            snippet=dict(
                title=options.yttitle,
                description=create_description(options, -1, -1, -1, -1, -1, -1,
                                               -1, -1),
                tags=tags,
                categoryId=options.category),
            status=dict(privacyStatus=options.privacy))

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(
            os.path.join(options.where + options.file),
            chunksize=10485760,
            resumable=True),
    )
    options.vid = upload(insert_request, options)
    return post_upload(options, mcode, youtube, spreadsheet)


def upload(insert_request, options):
    response = None
    ACCEPTABLE_ERRNO = (errno.EPIPE, errno.EINVAL, errno.ECONNRESET)
    try:
        ACCEPTABLE_ERRNO += (errno.WSAECONNABORTED, )
    except AttributeError:
        pass  # Not windows
    print(f"Uploading {options.file} of size {file_size(os.path.join(options.where + options.file))}")
    while True:
        try:
            status, response = insert_request.next_chunk()
            if status is not None:
                percent = Decimal(
                    int(status.resumable_progress) / int(status.total_size))
                print(f"{round(100 * percent, 2)}% uploaded")
        except HttpError as e:
            if e.resp.status in retry_status_codes:
                print("A retriable HTTP error {e.resp.status} occurred:\n{e.content}")
        except retry_exceptions as e:
            print(f"A retriable error occurred: {e}")

        except Exception as e:
            if e in ACCEPTABLE_ERRNO:
                print("Retriable Error occured, retrying now")
            else:
                print(e)
            pass
        # print("Status: ", end='')
        # print(status)
        if response:
            if "id" in response:
                print(
                    f"Video link is https://www.youtube.com/watch?v={response['id']}")
                return response['id']
            else:
                print(response)
                print(status)
                exit("Upload failed, no id in response")


def post_upload(options, mcode, youtube, spreadsheet):
    try:
        if "thumbnail.png" in options.files:
            update_thumbnail(youtube, options.vid,
                             os.path.join(options.where + "thumbnail.png"))
        else:
            print("thumbnail.png does not exist")

    except HttpError as e:
        if e.resp.status in retry_status_codes:
            error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"

    except retry_exceptions as e:
        error = f"A retriable error occurred: {e}"

    try:
        add_to_playlist(youtube, options.vid, options.pID)

    except Exception as e:
        print("Failed to post to playlist")

    if options.tba:
        request_body = json.dumps({mcode: options.vid})
        post_video(options.tbaID, options.tbaSecret, request_body,
                   options.ecode)
    elif options.ceremonies and options.post:
        request_body = json.dumps([options.vid])
        post_video(options.tbaID, options.tbaSecret, request_body,
                   options.ecode, "media")

    wasBatch = "True" if any(
        options.end != y for y in ("For batch uploads", "")) else "False"
    usedTBA = "True" if options.tba else "False"
    totalTime = dt.datetime.now() - options.then
    values = [[
        str(dt.datetime.now()),
        str(totalTime), f"https://www.youtube.com/watch?v={options.vid}", usedTBA, options.ename, wasBatch, mcode
    ]]
    sheetbody = {'values': values}
    try:
        spreadsheet.spreadsheets().values().append(
            spreadsheetId=spreadsheetID,
            range=rowRange,
            valueInputOption="USER_ENTERED",
            body=sheetbody).execute()
        print("Added data to spreadsheet")
    except Exception as e:
        print("Failed to write to spreadsheet")
    return f"DONE UPLOADING {options.file}\n"
