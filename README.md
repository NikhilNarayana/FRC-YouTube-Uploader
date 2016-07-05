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
* Automated Web Interface


## How to Setup for Web UI use
1. Install Python 2.7 for your OS
2. Clone this repository into the folder that will contain the videos
3. Install the requirements for the script with `pip install -r /path/to/requirements.txt`
4. Add the thumbnail to the above folder as `thumbnail.png`
5. Make your recording program follow this naming scheme: [EVENT_NAME] - [MATCH TYPE] ex. 2016 Indiana State Championship - Qualification Match 1. Also use the Tiebreaker scheme when necessary.
5. Start the program by running `python start.py`
6. Add in the necessary info.
7. Hit submit everytime a match finishes. No need to update Match Number unless you are entering eliminations.
8. Enjoy not having to deal with YouTube's front end 🎉

### Web UI Breakdown
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/6HuZ1sHrGR0/0.jpg)](http://www.youtube.com/watch?v=6HuZ1sHrGR0)

This demo shows a basic use of the application. In addition I have the data being sent to the backend shown in the console beforehand.

I focused on simplicty and usability. All the necessary details fit into one small space allowing you to easily place this anywhere on your screen without needing to see all of it.

##### Event Name
You can name this as you wish, but it should also be used at the start of every video filename.

##### Event Code
Find this at TheBlueAlliance in the address bar of the event page. It generally follows [YEAR]code format such as 2016arc.

##### Playlist ID
If you want to add your video to a playlist you can find the playlist ID on the playlist page's address. Every playlist ID starts with PL making them easy to identify.

##### TBA Event ID/Secret
Both of these must be obtained by contacting TBA at contact@thebluealliance.com for the keys to your event.

##### Video Description
The usual description used in the program is fairly lengthy, but provides a lot of links that may be useful. You will need to write in the `WEBSITE_LINK`, `TWITTER_HANDLE`, `FACEBOOK_NAME` in youtubeup.py if you want to make use of it though.

##### Match Number
Fairly self-explanatory, this value will increment each time you press "Submit" so you can forget about updating all the info for every match.

##### Last Match Number
If you want to batch upload a number of files you can do so with this. Every match including this number and `Match Number` will be uploaded and added to TBA. It will then replace this textbox with the original value and update Match Number to the last match uploaded + 1.

## How to Setup for CLI use
1. Install Python 2.7 for your OS
2. Clone this repository into the folder that will contain the videos
3. Install the requirements for the script with `pip install -r /path/to/requirements.txt`
4. Add the thumbnail to the above folder as `thumbnail.png`
5. Edit the code's default variables such as `DEFAULT_PLAYLIST_ID`, `EVENT_CODE` (from TBA), `EVENT_NAME` and `DEFAULT_DESCRIPTION`
6. Get the `client_secrets.json` file from here: https://console.developers.google.com/ by clicking API -> Create Credentials -> OAuth Client ID -> Other. Fill in the dialog with anything. Once finished click the newly created ID and download the JSON file. Remember to name it as `client_secrets.json`.
7. Get `X-TBA-Auth-Id` and `X-TBA-Auth-Sig` data by asking contact@thebluealliance.com for the event token and secret and set those values as `TBA_TOKEN` and `TBA_SECRET` respectively.
8. Run `python youtubeup.py` once to get YouTube Permissions authorized. Make sure you do it for the channel that you want to upload to.
9. Run `python youtubeup.py` and include the following parameters : `--mnum` (match number) and `--mcode`. `mcode` is a number that represents one of four values in a list ["qm", "qf", "sf", f"]. The list starts at 0 and goes to 3. `"qm"` is the default value.
10. Enjoy not having to deal with YouTube's front end 🎉

### CLI Examples
* Qualification Match 54: `python youtubeup.py --mnum 54`
* Qualification Matches 4 - 20: `python youtubeup.py --mnum 4 --end 20`
* Quarterfinal Match 3: `python youtubeup.py --mcode 1 --mnum 3`
* Quarterfinal Tiebreaker 3: `python youtubeup.py --mcode 1 --mnum 11`
* Semifinal Match 4: `python youtubeup.py --mcode 2 --mnum 4`
* Semifinal Tiebreaker 1: `python youtubeup.py --mcode 2 --mnum 5`
* Finals Match 1: `python youtubeup.py --mcode 3 --mnum 1`
* Finals Tiebreaker: `python youtubeup.py --mcode 3 -- mnum 3`

If you are still in need of assistance, feel free to contact me.


### Credits
* Google - Authentication and Video Uploading
* Phil Lopreiato - TBA Integration
* Wes Jordan - Python TBA API Layer (https://github.com/Thing342/pyTBA)
* Stack Exchange - Bug Fixes


## Extra Script
### updatePlaylistThumbnails.py
This script expects two inputs, a playlist ID (`--pID`) and a thumbnail file name (`--tnail`). It will then update every the thumbnails of every video in that playlist to the one you provide. This makes it simple to update older playlists with a new thumbnail so you can keep your look consistent.

This script is not used within youtubeup.py