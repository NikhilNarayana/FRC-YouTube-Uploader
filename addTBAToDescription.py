import web
from web import form
import youtubeup as yup
import argparse
import csv
from urlparse import *
from youtubeAuthenticate import *
import simplejson as json
import TBA
import pdb

render = web.template.render('webpage/')

urls = ('/', 'index')
app = web.application(urls, globals())
data = """Red Alliance (%s, %s, %s) - %s
Blue Alliance  (%s, %s, %s) - %s

"""
credits = """

Updated with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader)"""

def tbainfo(ecode, mcode):
	blue_data, red_data = TBA.get_match_results(ecode, mcode)
	print data % (blue_data[1], blue_data[2], blue_data[3], blue_data[0], 
		red_data[1], red_data[2], red_data[3], red_data[0])


def run(youtube, vURL, pID, ecode, mID, mnum, end):
	if end != "Only for batch updates":
		while int(mnum) <= int(end):
			vID = video_id(vURL)
			update_description(youtube, vID, ecode, mID, mnum)
			vURL = (str("https://www.youtube.com/watch?v=%s" % get_next_video_id(youtube, vID, pID)))
			mnum = int(mnum) + 1
		print "Updated all video descriptions"
		return vURL
	else:
		vID = video_id(vURL)
		update_description(youtube, vID, ecode, mID, mnum)
		vURL = (str("https://www.youtube.com/watch?v=%s" % get_next_video_id(youtube, vID, pID)))
		return vURL



#http://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
#Best way covering a variety of link styles
def video_id(value):
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return value

def get_next_video_id(youtube, vID, pID):
	next = False
	playlistitems_list = youtube.playlistItems().list(
		playlistId=pID,
		part="snippet",
		maxResults=50
	).execute()
	nextPageToken = playlistitems_list["nextPageToken"]
	while ('nextPageToken' in playlistitems_list):
		nextPageList = youtube.playlistItems().list(
				playlistId=pID,
				part="snippet",
				maxResults=50,
				pageToken=nextPageToken
			).execute()
		playlistitems_list["items"] = playlistitems_list["items"] + nextPageList["items"]
		if "nextPageToken" not in nextPageList:
			playlistitems_list.pop('nextPageToken', None)
		else:
			nextPageToken = nextPageList['nextPageToken']
	for playlist_item in playlistitems_list["items"]:
		if next is True:
			return playlist_item["snippet"]["resourceId"]["videoId"]
		if (playlist_item["snippet"]["resourceId"]["videoId"] == vID and next is False) and playlistitems_list["pageInfo"]["resultsPerPage"] <= playlist_item["snippet"]["position"]:
			next = True
	return None


def update_description(youtube, vID, ecode, mcode, mnum):
	snippet = youtube.videos().list(
			part="snippet",
			id=vID).execute()
	olddesc = snippet['items'][0]['snippet']['description']
	newdesc = data + olddesc + credits
	mcode = yup.get_match_code(mcode, int(mnum))
	blue_data, red_data = TBA.get_match_results(ecode, mcode)
	newdesc = newdesc % (red_data[1], red_data[2], red_data[3], red_data[0], 
		blue_data[1], blue_data[2], blue_data[3], blue_data[0])
	snippet['items'][0]['snippet']['description'] = newdesc
	response = youtube.videos().update(
		part='snippet', 
		body=dict(
			snippet=snippet['items'][0]['snippet'],
			id=vID)
		).execute()
	print "Updated description of %s" % vID

dataform = form.Form(
	form.Textbox("pID",
		form.regexp("^PL", "Must be a playlist ID, all of which start with 'PL'"),
		form.regexp("^\s*\S+\s*$", "Can not contain spaces."),
		description="Playlist ID",
		size=41),
	form.Textbox("vURL", description="Video URL", size=41),
	form.Textbox("ecode", description="Event Code (ex. 2016arc)"),
	form.Dropdown("mcode",
		[("qm", "Qualifications"), ("qf","Quarterfinals"), ("sf", "Semifinals"), ("f", "Finals")],
		description="Match Type"),
	form.Textbox("mnum",
		form.notnull,
		form.regexp("\d+", "Cannot contain letters"),
		form.Validator("Must be more than 0", lambda x:int(x)>0),
		description="Match Number"),
	form.Textbox("end", 
		description="Last Match Number", 
		value="Only for batch updates"),
		validators = [form.Validator("Last Match Number must be greater than Match Number", 
		lambda i: i.end == "Only for batch updates" or int(i.end) > int(i.mnum))])

class index:
	def GET(self):
		form = dataform()
		return render.forms(form)
	def POST(self):
		form = dataform()
		if not form.validates():
			return render.forms(form)
		youtube = get_authenticated_service()
		form.vURL.set_value(run(youtube, form.d.vURL, form.d.pID, form.d.ecode, form.d.mcode, form.d.mnum, form.d.end))
		if form.d.end == "Only for batch updates":
			form.mnum.set_value(str(int(form.d.mnum) + 1))
		else:
				form.mnum.set_value(str(int(form.d.end) + 1))
				form.end.set_value("Only for batch updates")
		return render.forms(form)

if __name__=="__main__":
	web.internalerror = web.debugerror
	app.run()