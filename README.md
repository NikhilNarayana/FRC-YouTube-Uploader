# FRC-CLI-YouTube-Uploader
[![Build Status](https://travis-ci.org/NikhilNarayana/FRC-YouTube-Uploader.svg?branch=master)](https://travis-ci.org/NikhilNarayana/FRC-YouTube-Uploader)

A YouTube Uploader with FRC Matches in mind.


## Current Feature Set:
* Upload Videos (single or batch uploads possible)
* Add Custom Thumbnails to a video
* Add to a YouTube Playlist
* Get match results from TBA and add them to the description
* Add videos to The Blue Alliance automatically
* Mostly Automated Web Interface
* Saves and Reads form values to and from CSV


## How to Setup
1. Install Python 2.7 for your OS
2. Clone this repository into the folder that will contain the videos
3. Install the requirements for the script with `pip install -r /path/to/requirements.txt`
4. Add the thumbnail to the same folder as `thumbnail.png`
5. Make your recording program follow this naming scheme: [EVENT_NAME] - [MATCH TYPE] ex. 2016 Indiana State Championship - Qualification Match 1. Also use the Tiebreaker scheme when necessary.
5. Start the program by running `python start.py` and navigating to `localhost:8080` in your browser
6. Add in the necessary info.
7. Hit submit everytime a match finishes. No need to update Match Number unless you are entering eliminations.
8. Enjoy not having to deal with YouTube's front end 🎉

### Web UI Breakdown
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/6HuZ1sHrGR0/0.jpg)](http://www.youtube.com/watch?v=6HuZ1sHrGR0)

This demo shows a basic use of the application. In addition I have the data being sent to the backend shown in the console beforehand.

I focused on simplicty and usability. All the necessary details fit into one small space allowing you to easily place this anywhere on your screen without needing to see all of it.

##### Event Name
You can name this as you wish, but it should also be used at the start of every video filename. Generally includes [YEAR] [NAME OF EVENT]

##### Event Code
Find this at TheBlueAlliance in the address bar of the event page. It generally follows [YEAR][EVENT_CODE] format such as 2016arc or 2016incmp.

##### Playlist ID
You can find the playlist ID on the playlist page's web address. Every playlist ID starts with PL making them easy to identify.

##### TBA Event ID/Secret
Both of these must be obtained by contacting TBA at contact@thebluealliance.com for the keys to your event.

##### Video Description
The usual description used in the program is fairly lengthy, but provides a lot of links that may be useful. You will need to write in the `WEBSITE_LINK`, `TWITTER_HANDLE`, `FACEBOOK_NAME` in youtubeup.py if you want to make use of it though.

##### Match Number
Fairly self-explanatory, this value will increment each time you press "Submit" so you can forget about updating all the info for every match.

##### Last Match Number
If you want to batch upload a number of files you can do so with this. Every match `Match Number` and this number inclusive will be uploaded and added to TBA. It will then replace this textbox with the original string and update Match Number to the last match uploaded + 1.

If you are still in need of assistance, feel free to contact me.


### Credits
* Google - Authentication and Video Uploading
* Phil Lopreiato - TBA Integration
* Wes Jordan - Python TBA API Layer (https://github.com/Thing342/pyTBA)
* Stack Exchange - Bug Fixes


## Extra Scripts
### updatePlaylistThumbnails.py
This script expects two inputs, a playlist ID (`--pID`) and a thumbnail file name (`--tnail`). It will then update every the thumbnails of every video in that playlist to the one you provide. This makes it simple to update older playlists with a new thumbnail so you can keep your look consistent.

### addTBAToDescription.py
addTBA will add match information to the video description retroactively. This script runs similarly to `start.py`. You start it with `python addTBAToDescription.py` and navigate to `localhost:8080` to use to script. You have to provide the video url, event code, and match code. Future goal is to add title to this

These scripts are not used within start.py
