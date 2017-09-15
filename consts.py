#! /usr/bin/env python

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
DEFAULT_DESCRIPTION = """Footage of the {ename} is courtesy of {team}.

Red Alliance  ({red1}, {red2}, {red3}) - {redscore}
Blue Alliance ({blue3}, {blue2}, {blue1}) - {bluescore}

To view match schedules and results for this event, visit The Blue Alliance Event Page: https://www.thebluealliance.com/event/{ecode}

Follow us on Twitter (@{twit}) and Facebook ({fb}).

For more information and future event schedules, visit our website: {weblink}

Thanks for watching!

Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""

NO_TBA_DESCRIPTION = """Footage of the {ename} Event is courtesy of the {team}.

Follow us on Twitter (@{twit}) and Facebook ({fb}).

For more information and future event schedules, visit our website: {weblink}

Thanks for watching!

Uploaded with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader) by Nikhil Narayana"""

VALID_PRIVACY_STATUSES = ("public", "unlisted", "private")

spreadsheetID = "18flsXvAcYvQximmeyG0-9lhYtb5jd_oRtKzIN7zQDqk"
rowRange = "Data!A1:G1"
response = None
status = None
error = None
sleep_minutes = 600
retry = 0
retryforlimit = 0
retry_status_codes = get_retry_status_codes()
retry_exceptions = get_retry_exceptions()
max_retries = get_max_retries()
tags = None
mcode = None
youtube = get_youtube_service()
spreadsheet = get_spreadsheet_service()
sizes = ["bytes", "KB", "MB", "GB", "TB"]