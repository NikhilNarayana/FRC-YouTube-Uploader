# FRC-CLI-YouTube-Uploader
[![Build Status](https://travis-ci.org/NikhilNarayana/FRC-CLI-Youtube-Uploader.svg?branch=develop)](https://travis-ci.org/NikhilNarayana/FRC-CLI-Youtube-Uploader)

A YouTube Uploader with FRC Matches in mind.


## Current Feature Set:
* Upload Videos (single or batch uploads possible)
* Add Custom Thumbnails to a video or even a whole playlist
* Add to Playlist(s)
* Get match results from TBA and add them to description
* Add videos to The Blue Alliance automatically
* Web Interface
* Automated 


## How to Setup for CLI use
1. Install Python 2.7 for your OS
2. Clone this repository into the folder that will contain the videos
3. Install the requirements for the script with `pip install -r /path/to/requirements.txt`
4. Add the thumbnail to the Thumbnails folder as `thumbnail.png`
5. Edit the code's default variables such as `DEFAULT_PLAYLIST_ID`, `EVENT_CODE` (from TBA), `EVENT_NAME` and `DEFAULT_DESCRIPTION`
6. Get the `client_secrets.json` file from here: https://console.developers.google.com/ by clicking API -> Create Credentials -> OAuth Client ID -> Other. Fill in the dialog with anything. Once finished click the newly created ID and download the JSON file. Remember to name it as `client_secrets.json`.
7. Get `X-TBA-Auth-Id` and `X-TBA-Auth-Sig` data by asking contact@thebluealliance.com for the event token and secret and set those values as `TBA_TOKEN` and `TBA_SECRET` respectively.
8. Run `python youtubeup.py` once to get YouTube Permissions authorized. Make sure you do it for the channel that you want to upload to.
9. Run `python youtubeup.py` and include the following parameters : `--mnum` (match number) and `--mcode`. `mcode` is a number that represents one of four values in a list ["qm", "qf", "sf", f"]. The list starts at 0 and goes to 3. `"qm"` is the default value.
10. Enjoy not having to deal with YouTube's front end 🎉

### Examples Usage(expects variables from 4 and 6 to be added in)
* Qualification Match 54: `python youtubeup.py --mnum 54`
* Qualification Matches 4 - 20: `python youtubeup.py --mnum 4 --end 20`
* Quarterfinal Match 3: `python youtubeup.py --mcode 1 --mnum 3`
* Quarterfinal Tiebreaker 3: `python youtubeup.py --mcode 1 --mnum 11`
* Semifinal Match 4: `python youtubeup.py --mcode 2 --mnum 4`
* Semifinal Tiebreaker 1: `python youtubeup.py --mcode 2 --mnum 5`
* Finals Match 1: `python youtubeup.py --mcode 3 --mnum 1`
* Finals Tiebreaker: `python youtubeup.py --mcode 3 -- mnum 3`

If you are still in need of assistance, feel free to contact me.


### Notes
Most of the code was built specifically for the 2016 Indiana State Championship, but I attempted to make it clear what needed to be changed for this to be used at any event. Ideally the future of this program will be a GUI that eliminates the need for any code changes and relies on the user to just feed it the info once per event.


### Credits
* Google - Authentication and Video Uploading
* Phil Lopreiato - TBA Integration
* Wes Jordan - TBA API Wrapper (http://wesj.org/documents/bluealliance.py)
* Stack Exchange - Bug Fixes


## Extra Script
### updatePlaylistThumbnails.py
This script expects two inputs, a playlist ID (`--pID`) and a thumbnail file name (`--tnail`). It will then update every the thumbnails of every video in that playlist to the one you provide. This makes it simple to update older playlists with a new thumbnail so you can keep your look consistent.

This script is not used within youtubeup.py
