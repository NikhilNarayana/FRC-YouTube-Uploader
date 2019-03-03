# FRC-YouTube-Uploader

A YouTube Uploader for FRC Events


## Contributing
PRs are appreciated and will be reviewed quickly, the only code quality standard I have is to follow PEP8 standard except for the line length. If you have trouble understanding my code just ask me.


## Current Feature Set:
* Upload Videos (single or batch uploads possible)
* Queue and Dequeue Videos to Upload
* Add to a YouTube Playlist
* Include match results from TBA in description
* Add videos links to The Blue Alliance
* Mostly Automated Interface
* Saves and Loads form values


## How to Setup
1. Install [Python 3.7.2](https://www.python.org/downloads/release/python-372/) for your OS with the PATH added and make sure there are no other versions of Python 3.
2. Install the program with `pip3 install -U FRCUploader`. If you want untested features you can download the repo and install with `pip3 install -U /path/to/repo`
3. Create a folder for storing your match videos.
4. Add the thumbnail to the match video folder as `thumbnail.png` (not required, but suggested).
5. Make your recording program follow this naming scheme: [MATCH TYPE] \(TIEBREAKER\) [MATCH NUM].[EXTENSION] ex. Qualification Match 1.mp4.
6. Start the program by running `frcuploader`.
7. Add in the necessary info in the Event Values and Match Values tabs
8. Hit submit every time a match finishes. No need to update any values unless you are entering eliminations or doing ceremonies.
9. Enjoy not having to deal with YouTube's front end 🎉.

### File Name Examples

File names are determined through substrings, you need the base of the match type and the match number at a minimum. Is this bad code design? Probably but it works and covers all known cases. Additionally all file names can be lowercase.
Bases:

    Qualification -> qual
    
    Quarter -> quarter + final
    
    Semifinal -> semi + final
    
    Final -> final
    
    Tiebreaker -> tiebreak

QM15 = `Qualification Match 15.mp4` or `Qual 15.mp4`

SF2M3 = `Semifinal Tiebreaker 2.mp4` or `semi final tiebreak 2.mp4`

F1M3 = `Final 3.mp4` or `final tiebreaker.mp4` (The FMS shows Final 3, but I allow either tiebreaker or 3 for naming)

Opening Ceremonies = `Friday Opening Ceremonies.mp4` or `Day 1 Opening Ceremony.mp4`

Closing Ceremonies = `Awards Ceremony.mp4` or `Closing Ceremonies.mp4`

Alliance Selection = `Alliance Selection.mp4` or `alliance selection.mp4`

Highlight Reel = `Highlight Reel.mp4` or `Wrapup Video.mp4`

## UI Breakdown
### Event Values
![alt text](https://i.imgur.com/m5He8Ki.png)

##### Match File Location
Select the root directory for files by clicking open and then navigating to the directory you would like to pull match videos from.

##### Get Newest File
If your recording program doesn't support setting the file names with the necessary info each time you can use this simply get the newest file in the directory instead. This is great for programs like OBS, XSplit, and vMix.

##### Production Team/Facebook Name/Twitter Handle/Website Link
Constants that used to be in the script itself, you can now edit them as you see fit without going into the code.

##### Event Name
You can name this as you wish, but know that it goes at the start of the video's YouTube Title, if you don't like this I can make a toggle. Generally includes [YEAR] [NAME OF EVENT]

##### Event Code
Find this at TheBlueAlliance in the address bar of the event page. It generally follows [YEAR][EVENT_CODE] format such as 2018arc or 2016incmp.

##### Playlist ID
You can find the playlist ID on the playlist page's web address. Every playlist ID starts with PL making them easy to identify. A full link will be shortened after you submit it.

##### TBA Event ID/Secret
www.thebluealliance.com/request/apiwrite

Both of these must be obtained by requesting them from the link above for the keys to your event. If your event is not on TBA I suggest you just uncheck `Use TBA`.

##### Video Privacy Status
Select the privacy status you would like to upload with. If your channel allows monetization and you would like to monetize the videos, you should set the privacy status to `unlisted` and then update monetization later.

##### Video Description
The description used in the program is fairly lengthy, but adds a lot of info that can be nice to have. If you would like to change the description you can rearrange it as you see fit, but you must keep anything in curly braces to prevent the program from blowing up in your face when you hit submit.

Right clicking on the `Video Description` title text will bring up a reset button if necessary.

### Match Values
![alt text](https://i.imgur.com/FVH3wx6l.png)

##### Match Code
This is hidden by default and can be accessed by toggling it in the menu bar.

This is an overriding function that will push any match you setup here to the correct TBA match and with the right info. This does not affect other parameters, you still need to set them up so it will find the correct match. For example, [2017 PCH Albany](https://www.thebluealliance.com/event/2017gaalb) had 5 replay matches in Semifinals 2, the matches that counted were matches 4-6 on TBA, but the FMS kept the naming scheme from matches 1-3. To fix this you can input the match info like it was for `SF2M1` and name the file `Semifinal Match 2.mp4`, but then set match code to `SF2M4`. That would get the right scores and then update the right TBA match. This should almost never be used outside of cases like this.

##### Match Number
Fairly self-explanatory, just remember to reset the value when you go into each stage of eliminations. This value will increment each time you press "Submit". Get the value from the FMS display during tiebreakers.

##### Ceremonies
All the non-default options in this dropdown will tell the program to ignore various parameters like `Match Number`. Uploading Alliance Selection will then update all the necessary form fields for entering elimination matches.
For Opening Ceremonies you need to have `Day X` or put the current day of the week (eg. `Friday`) in the file name.
For Closing Ceremonies you need to just have `Closing` or `Award` in the file name.
For Alliance Selection you need to have `Alliance` and `Selection` in the file name.
For Highlight Reels you need to have `Highlight` or `Wrapup` in the file name
All terms are matched in a substring so `Award` will match with `Awards` and same for others.

##### Event Day
This is in conjunction with the above option. If you are not uploading live this is very important, you need to name the ceremony files with Day 1, 2, or 3 based on when they were in your event. Then select the same value in this dropdown and the program will find the correct one. Only Opening and Closing Ceremonies are affected, there is only one Alliance Selection so it don't change anything for that. If you are uploading live, I suggest you leave this at `Ignore` and just set the file name to include the current day name.

##### Last Match Number
If you want to batch upload a number of files you can do so with this. Every match between `Match Number` and this number, inclusive, will be uploaded and added to TBA. It will then replace this field with 0 and update Match Number to the last match uploaded + 1.

### Status Output
![alt text](https://i.imgur.com/atKajjXl.png)

##### Output
This will display any information you need to know about an ongoing upload, the same info will be written to the command prompt as a backup and any errors will be written to a file in your root user directory. It is currently set to auto scroll to the bottom, but if you hit an infinite loop you can toggle the auto scrolling with the button.

##### Queue
The queue shows upcoming uploads with the top most item being the currently uploaded match.

Double clicking on a row in the Queue will remove it from the Queue. Be careful because you can't undo it unless you resubmit a new job.

#### Menu Bar
This is a bit different if you are on MacOS vs Windows. The menu bar is a part of the main window on Windows and it is a part of the native menu bar on MacOS.

##### Reset Form Values
Resets the form values to all the default values and resets the form value file.

##### Remove Youtube Credentials
Deletes the Youtube credentials and kills the program. Killing the program is intentional and necessary. You will be prompted for new credentials after you restart the program.

##### Show/Hide Match Code
Will toggle the match code's visiblity.

##### Toggle Uploads/Save Queue/Load Queue
These three options are meant to be used together to provide an easy way to upload matches after an event, especially if you choose to use `Get Newest File`. Before submitting any uploads, you should select `Toggle Uploads` and then just submit as necessary. You can choose to save the queue after every submission or save at the very end. When you decide to finally upload you can just open the program, select `Load Queue`, and wait for the uploads to finish. **Note** the filesystem and computer used to upload must be maintained for the uploads to work.

If you are still in need of assistance, feel free to contact me.

### Stats
Stats are collected on each match uploaded and can be found here: https://docs.google.com/spreadsheets/d/18flsXvAcYvQximmeyG0-9lhYtb5jd_oRtKzIN7zQDqk/edit?usp=sharing
All the information collected is very simple and lacks sensetive data. If you want to opt out let me know and I will finally build that button into the form.

### Credits
* Google - Authentication and Video Uploading
* Phil Lopreiato - TBA Trusted API Integration
* Wes Jordan - Python TBA API Layer (https://github.com/Thing342/pyTBA) *no longer used*
* tbapy -  New Python TBA API Layer
* Josh Klar - Bug Fixes during 2017 St. Joseph District
* Matthew Zacune - Testing and Feature Ideas
* The Internet - Bug Fixes


## Extra Scripts
All scripts are written in python 3 and can be called as arguments to the main script as listed below.

### updatePlaylistThumbnails.py (`frcuploader -t`)
This script will prompt for a playlist link and a file name for the thumbnail. It will then update every the thumbnails of every video in that playlist to the one you provide. This makes it simple to update older playlists with a new thumbnail so you can keep your look consistent.

### updateTBA.py (`frcuploader -u`)
Forcefully update thebluealliance.com with a match video. The prompts will ask you for the necessary links. If you want to post the event's opening ceremonies or other non-match videos please link to www.thebluealliance.com/event/[event_code]#media.

### playlistToTBA.py (`frcuploader -p`)
If for whatever reason you failed to post to TBA while using this uploader you can use this script afterwards to automatically link match videos to the event's page. Again the program will prompt you for links, once you do that it will take over and update TBA.
