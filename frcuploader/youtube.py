#!/usr/bin/env python3

try:
    import http.client as httplib
except ImportError:
    import httplib
import httplib2
import os
import sys
import errno
from time import sleep
from decimal import Decimal

from . import consts

from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from oauth2client.file import Storage
from oauth2client.tools import run_flow
from oauth2client.client import flow_from_clientsecrets

httplib2.RETRIES = 1

RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    httplib.NotConnected,
    httplib.IncompleteRead,
    httplib.ImproperConnectionState,
    httplib.CannotSendRequest,
    httplib.CannotSendHeader,
    httplib.ResponseNotReady,
    httplib.BadStatusLine,
)

RETRIABLE_STATUS_CODES = [500, 502, 504]

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_PARTNER_SCOPE = "https://www.googleapis.com/auth/youtubepartner"
SPREADSHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"

PREFIXES = (
    consts.root,
    sys.prefix,
    os.path.join(sys.prefix, "local"),
    "/usr",
    os.path.join("/usr", "local"),
)
SUFFIXES = (
    "client_secrets.json",
    ".client_secrets.json",
    os.path.join("share", consts.short_name, "client_secrets.json"),
)


def upload(yt, body, file, notify=False):
    vid = None
    ret = None
    retries = 0
    while not vid and retries < 10:
        insert_request = yt.videos().insert(
            part=",".join(body.keys()),
            body=body,
            notifySubscribers=notify,
            media_body=MediaFileUpload(file, chunksize=104857600, resumable=True),
        )
        ret, vid = upload_service(insert_request)
        retries += 1
    return ret, vid


def upload_service(insert_request):
    response = None
    retry_exceptions = RETRIABLE_EXCEPTIONS
    retry_status_codes = RETRIABLE_STATUS_CODES
    ACCEPTABLE_ERRNO = (errno.EPIPE, errno.EINVAL, errno.ECONNRESET)
    try:
        ACCEPTABLE_ERRNO += (errno.WSAECONNABORTED,)
    except AttributeError:
        pass  # Not windows
    while True:
        try:
            status, response = insert_request.next_chunk()
            if status is not None:
                percent = Decimal(
                    int(status.resumable_progress) / int(status.total_size)
                )
                print(f"{round(100 * percent, 2)}% uploaded")
        except HttpError as e:
            if e.resp.status in retry_status_codes:
                print(f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}")
            elif b"503" in e.content:
                print("Backend Error: will attempt to retry upload")
                return False, None
            elif b"uploadLimitExceeded" in e.content:
                print("You have exceeded the YouTube Upload Limit")
                print("Waiting 10 minutes before retrying to avoid the limit")
                sleep(600)
            else:
                print(e)
                return False, None
        except retry_exceptions as e:
            print(f"A retriable error occurred: {e}")

        except Exception as e:
            if e in ACCEPTABLE_ERRNO:
                print("Retriable Error occured, retrying now")
            else:
                print(e)
            pass
        if response:
            if "id" in response:
                print(f"Video link is https://www.youtube.com/watch?v={response['id']}")
                return True, response["id"]
            else:
                print(response)
                print(status)
                return False, None


def get_service(scope, service, secret=None):
    CLIENT_SECRETS_FILE = get_secrets(PREFIXES, SUFFIXES) if not secret else secret

    print(f"Using {CLIENT_SECRETS_FILE}")

    if not CLIENT_SECRETS_FILE:
        return None

    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=scope)

    flow.user_agent = consts.long_name
    storage = Storage(
        os.path.join(consts.root, f".{consts.abbrv}-oauth2-{service}.json")
    )
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return credentials


def get_youtube_service():
    credentials = get_service(YOUTUBE_UPLOAD_SCOPE, "youtube")

    if not credentials:
        return None

    http = httplib2.Http()
    try:
        # https://github.com/googleapis/google-api-python-client/issues/803
        http.redirect_codes = set(http.redirect_codes) - {308}
    except:
        pass

    return build("youtube", "v3", http=credentials.authorize(http))


def add_to_playlist(pID, vID):
    consts.youtube.playlistItems().insert(
        part="snippet",
        body=dict(
            snippet=dict(
                playlistId=pID, resourceId=dict(kind="youtube#video", videoId=vID)
            )
        ),
    ).execute()
    print("Added to playlist")


def get_secrets(prefixes, relative_paths):
    """
    Taken from https://github.com/tokland/youtube-upload/blob/master/youtube_upload/main.py
    Get the first existing filename of relative_path seeking on prefixes directories.
    """
    paths_attempted = []
    try:
        return os.path.join(sys._MEIPASS, relative_paths[-1])
    except Exception:
        for prefix in prefixes:
            for relative_path in relative_paths:
                path = os.path.join(prefix, relative_path)
                paths_attempted.append(path)
                if os.path.exists(path):
                    return path
        else:
            print(f"Unable to find client_secrets.json. Checked in {paths_attempted}")
            return None
