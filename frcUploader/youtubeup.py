#!/usr/bin/python

import os
import random
import sys
import time as ntime
import argparse

from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from TBA import *
from tbaAPI import *
from addtoplaylist import add_video_to_playlist
from updateThumbnail import update_thumbnail
from youtubeAuthenticate import *
from datetime import *
import threading

# Default Variables
DEFAULT_VIDEO_CATEGORY = 28
DEFAULT_THUMBNAIL = "thumbnail.png"
DEFAULT_TAGS = """%s, FIRST, omgrobots, FRC, FIRST Robotics Competition, robots, Robotics, FIRST Stronghold"""
QUAL = "Qualification Match %s"
QUARTER = "Quarterfinal Match %s"
QUARTERT = "Quarterfinal Tiebreaker %s"
SEMI = "Semifinal Match %s"
SEMIT = "Semifinal Tiebreaker %s"
FINALS = "Final Match %s"
FINALST = "Final Tiebreaker"
DEFAULT_DESCRIPTION = """Footage of the %s %s Event is courtesy of the %s.

Red Alliance (%s, %s, %s) - %s
Blue Alliance (%s, %s, %s) - %s

To view match schedules and results for this event, visit The Blue Alliance Event Page: https://www.thebluealliance.com/event/%s

Follow us on Twitter (@%s) and Facebook (%s).

For more information and future event schedules, visit our website: %s

Thanks for watching!"""

NO_TBA_DESCRIPTION = """Footage of the %s Event is courtesy of the %s.

Follow us on Twitter (@%s) and Facebook (%s).

For more information and future event schedules, visit our website: %s

Thanks for watching!"""

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def quals_yt_title(options):
	return options.ename + " - " + QUAL % options.mnum

def quarters_yt_title(options):
	if options.mnum <= 8 and options.mnum >= 1:
		title = options.ename + " - " + QUARTER % options.mnum
		return title
	elif options.mnum >= 9 and options.mnum <= 12:
		mnum = int(options.mnum) - 8
		title = options.ename + " - " + QUARTERT % str(mnum)
		return title
	else:
		raise ValueError("options.mnum must be within 1 and 12")

def semis_yt_title(options):
	if options.mnum <= 4 and options.mnum >= 1:
		title = options.ename + " - " + SEMI % options.mnum
		return title
	elif options.mnum >= 5 and options.mnum <= 6:
		mnum = int(options.mnum) - 4
		title = options.ename + " - " + SEMIT % str(mnum)
		return title
	else:
		raise ValueError("options.mnum must be within 1 and 6")

def finals_yt_title(options):
	if options.mnum <= 2 and options.mnum >= 1:
		title = options.ename + " - " + FINALS % options.mnum
		return title
	elif options.mnum == 3:
		title = options.ename + " - " + FINALST
		return title
	else:
		raise ValueError("options.mnum must be within 1 and 3")

def create_title(options):
	switcher = {
		"qm": quals_yt_title,
		"qf": quarters_yt_title,
		"sf": semis_yt_title,
		"f1m": finals_yt_title,
	}
	return switcher[options.mcode](options)

def quals_filename(options):
	return options.ename + " - " + QUAL % options.mnum + options.ext

def quarters_filename(options):
	if options.mnum <= 8 and options.mnum >= 1:
		filename = options.ename + " - " + QUARTER % options.mnum + options.ext
		return str(filename)
	elif options.mnum >= 9 and options.mnum <= 12:
		mnum = int(options.mnum) - 8
		filename = options.ename + " - " + QUARTERT % str(mnum) + options.ext
		return str(filename)
	else:
		raise ValueError("mnum must be between 1 and 12")

def semis_filename(options):
	if options.mnum <= 4 and options.mnum >= 1:
		filename = options.ename + " - " + SEMI % options.mnum + options.ext
		return str(filename)
	elif options.mnum >= 5 and options.mnum <= 6:
		mnum = int(options.mnum) - 4
		filename = options.ename + " - " + SEMIT % str(mnum) + options.ext
		return str(filename)
	else:
		raise ValueError("mnum must be between 1 and 6")

def finals_filename(options):
	if options.mnum <= 2 and options.mnum >= 1:
		filename = options.ename + " - " + FINALS % options.mnum + options.ext
		return str(filename)
	elif options.mnum == 3:
		filename = options.ename + " - " + FINALST + options.ext
		return str(filename)
	else:
		raise ValueError("mnum must be between 1 and 3")

def create_filename(options):
	switcher = {
		"qm": quals_filename,
		"qf": quarters_filename,
		"sf": semis_filename,
		"f1m": finals_filename,
	}
	return switcher[options.mcode](options)

def quals_match_code(mcode, mnum):
	match_code = str(mcode) + str(mnum)
	return match_code

def quarters_match_code(mcode, mnum):
	match_set = mnum % 4
	if match_set == 0:
		match_set = 4
	if mnum <= 4:
		match = 1
		match_code = mcode + str(match_set) + "m" + str(match)
		return match_code
	elif mnum > 4 and mnum <= 8:
		match = 2
		match_code = mcode + str(match_set) + "m" + str(match)
		return match_code
	elif mnum > 8 and mnum <= 12:
		match = 3
		match_code = mcode + str(match_set) + "m" + str(match)
		return match_code
	else:
		raise ValueError("mnum can't be larger than 12")

def semis_match_code(mcode, mnum):
	match_set = mnum % 2
	if match_set == 0:
		match_set = 2
	if mnum <= 2:
		match = 1
		match_code = mcode + str(match_set) + "m" + str(match)
		return match_code
	elif mnum > 2 and mnum <= 4:
		match = 2
		match_code = mcode + str(match_set) + "m" + str(match)
		return match_code
	elif mnum > 4 and mnum <= 6:
		match = 3
		match_code = mcode + str(match_set) + "m" + str(match)
		return match_code
	else:
		raise ValueError("mnum can't be larger than 6")

def finals_match_code(mcode, mnum):
	if mnum > 3:
		raise ValueError("mnum can't be larger than 3")
	match_code = str(mcode) + str(mnum)
	return match_code

def get_match_code(mcode, mnum):
	switcher = {
		"qm": quals_match_code,
		"qf": quarters_match_code,
		"sf": semis_match_code,
		"f1m": finals_match_code,
	}
	return switcher[mcode](mcode, mnum)

def tba_results(options):
	mcode = get_match_code(options.mcode, int(options.mnum))
	blue_data, red_data = get_match_results(options.ecode, mcode)
	return blue_data, red_data, mcode

def create_description(options, blue1, blue2, blue3, blueScore, red1, red2, red3, redScore):
	if options.ddescription == False:
		return options.description
	credits = """

		Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""
	if all(x <= -1 for x in (red1, red2, red3, redScore, blue1, blue2, blue3, blueScore)):
		return options.description % (options.ename, options.prodteam, options.twit, options.fb, options.weblink) + credits
	try:
		return options.description % (options.ename, get_event_type(options.ecode), options.prodteam,
			red1, red2, red3, redScore, blue1, blue2, blue3, blueScore,
			options.ecode, options.twit, options.fb, options.weblink) + credits
	except TypeError, e:
		return description

def tiebreak_mnum(mnum, mcode):
	switcher = {
		"qf": int(mnum) + 8,
		"sf": int(mnum) + 4,
		"f1m": 3,
	}
	return switcher[mcode]

def upload_multiple_videos(youtube, spreadsheet, options):
	while int(options.mnum) <= int(options.end):
		try:
			thr1 = threading.Thread(target=initialize_upload, args=(youtube, spreadsheet, options))
			options.mnum = int(options.mnum) + 1
			thr2 = threading.Thread(target=initialize_upload, args=(youtube, spreadsheet, options))
			options.mnum = int(options.mnum) + 1
			thr1.daemon = True
			thr2.daemon = True
			thr1.start()
			ntime.sleep(20)
			thr2.start()
			thr1.join()
			thr2.join()
		except HttpError, e:
			print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
		print ""
		options.mnum = int(options.mnum) + 1
	print "All matches have been uploaded"

def init(args): #intializng all the variables where necessary and parsing data to create proper namespace fields
	args.tags = DEFAULT_TAGS
	args.privacyStatus = 0
	args.category = DEFAULT_VIDEO_CATEGORY
	if args.tba is True: #Specific changes for if using TBA
		TBA_ID = args.tbaID
		TBA_SECRET = args.tbaSecret
		if args.description == "Add alternate description here.":
			args.ddescription = True
			args.description = DEFAULT_DESCRIPTION
	if args.tba is False: #Specific changes for if not using TBA
		TBA_ID = -1
		TBA_SECRET = -1
		if args.description == "Add alternate description here.":
			args.ddescription = True
			args.description = NO_TBA_DESCRIPTION
	args.dtags = True if args.tags == DEFAULT_TAGS else False
	if args.dtags:
		args.tags = args.tags % args.ecode
	if args.tiebreak is True:
		args.mnum = tiebreak_mnum(args.mnum, args.mcode)

	youtube = get_youtube_service()
	spreadsheet = get_spreadsheet_service()

	args.file = create_filename(args)
	args.title = create_title(args)
	if os.path.isfile(args.file): #Check to make sure the file exists before continuing
		if type(args.end) is int: #if args.end is a string you can run this
			if int(args.end) > int(args.mnum):
				upload_multiple_videos(youtube, spreadsheet, args)
		else:
			try:
				initialize_upload(youtube, spreadsheet, args)
			except HttpError, e:
				print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
	else: raise ValueError("The file doesn't exist, please check the name schema for more info")

def initialize_upload(youtube, spreadsheet, options):
	print "Initializing upload for %s match %s" % (options.mcode, options.mnum)
	tags = None
	if options.tba:
		blue_data, red_data, mcode = tba_results(options)

		if options.dtags:
			tags = options.tags.split(",")
			tags.append("frc" + str(blue_data[1]))
			tags.append("frc" + str(blue_data[2]))
			tags.append("frc" + str(blue_data[3]))
			tags.append("frc" + str(red_data[1]))
			tags.append("frc" + str(red_data[2]))
			tags.append("frc" + str(red_data[3]))
			tags.append(get_event_hashtag(options.ecode))

		body = dict(
			snippet=dict(
				title=options.title,
				description=create_description(options, blue_data[1], blue_data[2], blue_data[3], blue_data[0],
												   red_data[1], red_data[2], red_data[3], red_data[0]),
				tags=tags,
				categoryId=options.category
			),
			status=dict(
				privacyStatus=VALID_PRIVACY_STATUSES[options.privacyStatus]
			)
		)
	else:
		mcode = get_match_code(options.mcode, int(options.mnum))

		if options.tags:
			tags = options.tags.split(",")
			tags.append(get_event_hashtag(options.ecode))

		body = dict(
			snippet=dict(
				title=options.title,
				description=create_description(options, -1, -1, -1, -1, -1, -1, -1, -1),
				tags=tags,
				categoryId=options.category
			),
			status=dict(
				privacyStatus=VALID_PRIVACY_STATUSES[options.privacyStatus]
			)
		)
	insert_request = youtube.videos().insert(
			part=",".join(body.keys()),
			body=body,
			media_body=MediaFileUpload(options.where+create_filename(options), chunksize=-1, resumable=True)
		)

	resumable_upload(insert_request, options, mcode, youtube, spreadsheet)

def resumable_upload(insert_request, options, mcode, youtube, spreadsheet):
	response = None
	error = None
	retry = 0
	retry_status_codes = get_retry_status_codes()
	retry_exceptions = get_retry_exceptions()
	max_retries = get_max_retries()
	while response is None:
		try:
			print "Uploading file..."
			status, response = insert_request.next_chunk()
			if 'id' in response:
				print "Video id '%s' was successfully uploaded." % response['id']
				print "Video link is https://www.youtube.com/watch?v=%s" % response['id']
				update_thumbnail(youtube, response['id'], "thumbnail.png")
				print "Video thumbnail added"
				add_video_to_playlist(
					youtube, response['id'], options.pID)
				request_body = json.dumps({mcode: response['id']})
				if options.tba is True:
					post_video(options.tbaID, options.tbaSecret, request_body, options.ecode)
				totalTime = datetime.now() - options.then
				spreadsheetID = "18flsXvAcYvQximmeyG0-9lhYtb5jd_oRtKzIN7zQDqk"
				rowRange = "Data!A1:F1"
				if type(options.end) is int: wasBatch = "True"
				else: wasBatch = "False"
				values = [[str(datetime.now()),str(totalTime)[1:],"https://www.youtube.com/watch?v=%s" % response['id'], str(options.tba), options.ename, wasBatch]]
				body = {'values': values}
				appendSpreadsheet = spreadsheet.spreadsheets().values().append(spreadsheetId=spreadsheetID, range=rowRange, valueInputOption="RAW", body=body).execute()
			else:
				exit("The upload failed with an unexpected response: %s" %
					 response)
		except HttpError, e:
			if e.resp.status in retry_status_codes:
				error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
																	 e.content)
			else:
				raise
		except retry_exceptions, e:
			error = "A retriable error occurred: %s" % e

		if error is not None:
			print error
			retry += 1
			if retry > max_retries:
				exit("No longer attempting to retry.")

			max_sleep = 2 ** retry
			sleep_seconds = random.random() * max_sleep
			print "Sleeping %f seconds and then retrying..." % sleep_seconds
			ntime.sleep(sleep_seconds)