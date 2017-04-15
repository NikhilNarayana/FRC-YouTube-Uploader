# FRC-CLI-YouTube-Uploader
[![Build Status](https://travis-ci.org/NikhilNarayana/FRC-YouTube-Uploader.svg?branch=master)](https://travis-ci.org/NikhilNarayana/FRC-YouTube-Uploader)

A YouTube Uploader for FRC Events


## Current Feature Set:
* Asynchronously Upload Videos (single or batch uploads possible)
* Add to a YouTube Playlist
* Include match results from TBA in description
* Add videos links to The Blue Alliance automatically
* Mostly Automated, Non-Blocking Web Interface
* Saves and Reads form values to and from CSV


## How to Setup
1. Install Python 2.7 for your OS with the PATH added and make sure there are no other versions of python 2.7
2. Download this repository into a subfolder to the folder that will contain the videos, make sure every event is in seperate folders
3. Install the requirements for the script with `pip install -r /path/to/requirements.txt`, or `make` if supported by your OS
4. Add the thumbnail to the same folder as `thumbnail.png`
5. Make your recording program follow this naming scheme: [MATCH TYPE] [MATCH NUM].[EXTENSION] ex. Qualification Match 1.mp4 Also use the Tiebreaker scheme when necessary
5. Start the program by executing the .bat file for Windows or .sh file for Linux/macOS or by running `python start.py`
6. Add in the necessary info
7. Hit submit everytime a match finishes. No need to update any values unless you are entering eliminations or doing ceremonies
8. Enjoy not having to deal with YouTube's front end 

### File Name Examples
QM15 = `Qualification Match 15.mp4` or `Qual 15.mp4`

SF2M3 = `Semifinal Tiebreaker 2.mp4` or `semi final tiebreak 2.mp4`

F1M3 = `Final 3.mp4` or `final tiebreaker.mp4` (The FMS shows Final 3, but I allow either tiebreaker or 3 for naming)

Opening Ceremonies = `Friday Opening Ceremonies.mp4` or `Day 1 Opening Ceremony.mp4`

Closing Ceremonies = `Awards Ceremony.mp4` or `Closing Ceremonies.mp4`

Alliance Selection = `Alliance Selection.mp4` or `alliance selection.mp4`

### Web UI Breakdown
![alt text](http://i.imgur.com/IYaJSex.png?1)

I focused on simplicty and usability. All the necessary details fit into one small space allowing you to easily place this anywhere on your screen without needing to see all of it.

##### Match File Locations
You can now pick whether the match files  are in the same folder as the scripts or the one above. Default is the one above (parent folder).

##### Production Team/Facebook Name/Twitter Handle/Website Link
Constants that used to be in the script itself, you can now edit them as you see fit without going into the code.

##### Event Name
You can name this as you wish, but it should also be used at the start of every video filename. Generally includes [YEAR] [NAME OF EVENT]

##### Event Code
Find this at TheBlueAlliance in the address bar of the event page. It generally follows [YEAR][EVENT_CODE] format such as 2016arc or 2016incmp.

##### Playlist ID
You can find the playlist ID on the playlist page's web address. Every playlist ID starts with PL making them easy to identify.

##### TBA Event ID/Secret
Both of these must be obtained by requesting them from www.thebluealliance.com/request/apiwrite for the keys to your event. If your event is not on TBA I suggest you just set `Update TBA` to False.

##### Video Description
The description used in the program is fairly lengthy, but adds a lot of info that can be nice to have. The usual description is found in `youtubeup.py`. If you would rather not use that description feel free to input your own or ask me to create a specific description just for you.

##### Match Code
This is an overriding function that will push any match you setup here to the correct TBA match and with the right info. This does not affect other parameters, you still need to set them up so it will find the correct match. For example, [2017 PCH Albany](https://www.thebluealliance.com/event/2017gaalb) had 6 matches in Semifinals 2, the matches that counted were matches 4-6 on TBA, but the FMS kept the naming scheme from matches 1-3. To fix this you can input the match info like it was for `SF2M1` and name the file `Semifinal Match 2.mp4`, but then set match code to `SF2M4`. That would get the right scores and then update the right TBA match.

##### Match Number
Fairly self-explanatory, just remember to reset the value when you go into each stage of eliminations. This value will increment each time you press "Submit". Get the value from the FMS display during tiebreakers.

##### Ceremonies
All the non-default options in this dropdown will tell the program to ignore various parameters like `Match Number`. Uploading Alliance Selection will then update all the necessary form fields for entering elimination matches.
For Opening Ceremonies you need to have `Day X` or put the current day of the week (eg. `Friday`) in the file name.
For Closing Ceremonies you need to just have `Closing` or `Award` in the file name.
For Alliance Selection you need to have the words `Alliance` and `Selection` in the file name.
All terms are matched in a substring so `Award` will match with `Awards` and same for others.

##### Last Match Number
If you want to batch upload a number of files you can do so with this. Every match between `Match Number` and this number, inclusive, will be uploaded and added to TBA. It will then replace this textbox with the original string and update Match Number to the last match uploaded + 1.

If you are still in need of assistance, feel free to contact me.

### Stats
Stats are collected on each match uploaded and can be found here: https://docs.google.com/spreadsheets/d/18flsXvAcYvQximmeyG0-9lhYtb5jd_oRtKzIN7zQDqk/edit?usp=sharing
All the information collected is very simple and lacks sensetive data. If you want to opt out let me know and I will finally build that button into the form.

### Credits
* Google - Authentication and Video Uploading
* Phil Lopreiato - TBA Integration
* Wes Jordan - Python TBA API Layer (https://github.com/Thing342/pyTBA)
* Josh Klar - Bug Fixes during 2017 St. Joseph District
* Matthew Zacune - Testing
* Stack Exchange - Bug Fixes


## Extra Scripts
### updatePlaylistThumbnails.py
This script expects two inputs, a playlist ID (`--pID`) and a thumbnail file name (`--tnail`). It will then update every the thumbnails of every video in that playlist to the one you provide. This makes it simple to update older playlists with a new thumbnail so you can keep your look consistent.

### addTBAToDescription.py
addTBA will add match information to the video description retroactively. This script runs similarly to `start.py`. You start it with `python addTBAToDescription.py` and navigate to `localhost:8080` to use to script. You have to provide the video url, event code, and match code.

These scripts are not used within start.py
