# FRC-CLI-YouTube-Uploader
CLI based YouTube Uploader with FRC in mind.
A lot of this is mashed together code that is reliable, but not very easy to use because it is CLI based and you have to edit the code for it to work at your events. 

The reasoning behind this project is that I don't want to copy over titles and descriptions for nearly 100 videos. This speeds up the process and in turn has grown to include a few features I didn't think of when I first started working on this.

## Project Structure
The main script is `youtubeup.py` which works by calling functions from the other scripts. The only other script that would need to be used on its own is `updatePlaylistThumbnails.py`, check the bottom for more details.

Main Script | Called Script(s) |  |  |  |  | 
--- | --- | --- | --- | --- | --- | ---
| youtubeup.py | youtubeAuthenticate.py | addtoplaylist.py | updateThumbnail.py | TBA.py | bluealliance.py |
| updatePlaylistThumbnails.py | updatethumbnail.py | youtubeAuthenticate.py |
| addtoplaylist.py | youtubeAuthenticate.py |
| updatethumbnail.py | youtubeAuthenticate.py |

## How to Setup
1. Install Python 2.7 for your OS
2. Install the requirements for the script with `pip install -r /path/to/requirements.txt`
3. Add the thumbnail to the Thumbnails folder as `thumbnail.png`
4. Edit the code's default variables such as `DEFAULT_PLAYLIST_ID`, `EVENT_CODE` (from TBA), `EVENT_NAME` and `DEFAULT_DESCRIPTION`
5. Get the `client_secrets.json` file from here: https://console.developers.google.com/ by clicking API -> Create Credentials -> OAuth Client ID -> Other. Fill in the dialog with anything. Once finished click the newly created ID and download the JSON file. Remember to name it as `client_secrets.json`.
6. Get `X-TBA-Auth-Id` and `X-TBA-Auth-Sig` data by asking contact@thebluealliance.com for the event token and secret and set those values as `TBA_TOKEN` and `TBA_SECRET` respectively.
7. Run `python youtubeup.py` once to get YouTube Permissions authorized. Make sure you do it for the channel that you want to upload to.
8. Run `python youtubeup.py` and include the following parameters : `--mnum` (match number) and `--mcode`. `mcode` is a number that represents one of four values in a list ["qm", "qf", "sf", f"]. The list starts at 0 and goes to 3. `"qm"` is the default value.
8. Enjoy not having to deal with YouTube's front end 🎉

### Examples Usage(expects variables from 4 and 6 to be added in)
* Qualification Match 54: `python youtubeup.py --mnum 54`
* Quarterfinal Match 3: `python youtubeup.py --mcode 1 --mnum 3`
* Quarterfinal Tiebreaker 3: `python youtubeup.py --mcode 1 --mnum 11`
* Semifinal Match 4: `python youtubeup.py --mcode 2 --mnum 4`
* Semifinal Tiebreaker 1: `python youtubeup.py --mcode 2 --mnum 5`
* Finals Match 1: `python youtubeup.py --mcode 3 --mnum 1`
* Finals Tiebreaker: `python youtubeup.py --mcode 3 -- mnum 3`

If you are still in need of assistance, feel free to contact me.

## Current Feature Set:
* Upload Videos
* Add Custom Thumbnails to a video or even a whole playlist
* Add to Playlist(s)
* Get match results from TBA and add them to description
* Add videos to The Blue Alliance automatically

Things to do in the future:
* GUI
* Automate everything so only a single human input is required

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

This script is not used within the main youtubeup.py
