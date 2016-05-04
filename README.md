# FRC-CLI-Youtube-Uploader
CLI based Youtube Uploader with FRC in mind.
A lot of this is mashed together code that is reliable, but not very easy to use because it is CLI based and you have to edit the code for it to work at your events. 

The reasoning behind this creation is that I don't want to copy over every single title and description for nearly 100 videos. So this was created to speed up the process and in turn has grown to include a few features I didn't think of when I first started working on this.

## How to Setup
1. Install Python 2.7 for your OS
2. Install the requirements for the script with `pip install -r /path/to/requirements.txt`
3. Add the thumbnail to the Thumbnails folder as `thumbnail.png`
4. Edit the code's default variables such as `TBA_TOKEN`, `TBA_SECRET`, `DEFAULT_PLAYLIST_ID`, `EVENT_CODE` (from TBA), `EVENT_NAME` and `DEFAULT_DESCRIPTION`
5. Run the script once to get Youtube Permissions.
6. Enjoy not having to deal with YouTube's front end 🎉

## Current Feature Set:
* Upload Videos
* Add Custom Thumbnails to a video or even a whole playlist
* Add to Playlist(s)
* Get video link for The Blue Alliance
* Get match results from TBA (Have yet to test during an event)
* Add videos to The Blue Alliance automatically (Have yet to test during an event)

Things to do in the future:
* GUI
* Automate everything so only a single human input is required

### Notes
Most of the code was built specifically for the 2016 Indiana State Championship, but I attempted to make it clear what needed to be changed for this to be used at any event.
