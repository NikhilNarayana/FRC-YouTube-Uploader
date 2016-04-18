import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


#Default Variables
CHANNEL_ID = "UCy2Lh8b-y0r-35LlcjOPPzw"
#How to get Channel ID
#If you have not applied for a custom channel address you can find it by going to your channel page and looking at the URL for the last part
#https://www.youtube.com/channel/XXXXXXXXXXXXXXXXXXXXXXXX/ It will look something like that. The number of characters will not be the same.
#If that doesn't work. The following link will be able to get it: http://johnnythetank.github.io/youtube-channel-name-converter/

DEFAULT_PLAYLIST_ID = "PL9UFVOe2UANx7WGnZG57BogYFKThwhIa2"
#How to get Playlist ID:
#https://developers.google.com/apis-explorer/#p/youtube/v3/youtube.playlists.list?part=snippet%252CcontentDetails&channelId=UC_x5XG1OV2P6uZZ5FSM9Ttw
#Go to the link above, replace the Channel ID with your own, go to the bottom and find the ID of the playlist you want.


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Cloud Console at
# https://cloud.google.com/console.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

CLIENT_SECRETS_FILE = "add_to_playlist_client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

%s

with information from the Cloud Console
https://cloud.google.com/console

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))


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

if __name__ == '__main__':
    argparser.add_argument("--vID",required=True,help="Video ID to add to playlist")
    args = argparser.parse_args()
    youtube = get_authenticated_service()
    add_video_to_playlist(youtube,args.vID,DEFAULT_PLAYLIST_ID)
    print "Added to playlist"