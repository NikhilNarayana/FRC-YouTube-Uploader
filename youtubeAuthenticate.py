#!/usr/bin/python

import httplib
import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

httplib2.RETRIES = 1

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
						httplib.IncompleteRead, httplib.ImproperConnectionState,
						httplib.CannotSendRequest, httplib.CannotSendHeader,
						httplib.ResponseNotReady, httplib.BadStatusLine)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = "client_secrets.json"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
								   CLIENT_SECRETS_FILE))

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

YOUTUBE_UPLOAD_SCOPE = """https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.force-ssl"""


def get_authenticated_service(args):
	flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
								   scope=YOUTUBE_UPLOAD_SCOPE,
								   message=MISSING_CLIENT_SECRETS_MESSAGE)

	storage = Storage("%s-oauth2.json" % sys.argv[0])
	credentials = storage.get()

	flags = argparser.parse_args(args=[])

	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage, flags)

	return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
				 http=credentials.authorize(httplib2.Http()))


def get_retry_status_codes():
	return RETRIABLE_STATUS_CODES


def get_retry_exceptions():
	return RETRIABLE_EXCEPTIONS


def get_max_retries():
	return 10