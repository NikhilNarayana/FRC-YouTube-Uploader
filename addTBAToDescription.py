import web
from web import form
import youtubeup as yup
import argparse
import csv
from urlparse import *
from youtubeAuthenticate import *
import simplejson as json
import TBA

render = web.template.render('webpage/')

urls = ('/', 'index')
app = web.application(urls, globals())
data = """Alliance (Team1, Team2, Team3) - Score
Blue Alliance (%s, %s, %s) - %s
Red Alliance  (%s, %s, %s) - %s

"""
credits = """

Updated with FRC-Youtube-Uploader (https://github.com/NikhilNarayana/FRC-YouTube-Uploader)"""

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
    return None

def update_description(youtube, vID, ecode, mcode):
	snippet = youtube.videos().list(
			part="snippet",
			id=vID).execute()
	olddesc = snippet['items'][0]['snippet']['description']
	newdesc = data + olddesc + credits
	blue_data, red_data = TBA.get_match_results(ecode, mcode)
	newdesc = newdesc % (blue_data[1], blue_data[2], blue_data[3], blue_data[0], 
		red_data[1], red_data[2], red_data[3], red_data[0])
	snippet['items'][0]['snippet']['description'] = newdesc
	response = youtube.videos().update(part='snippet', body=dict(snippet=snippet['items'][0]['snippet'], id=vID)).execute()
	print response

dataform = form.Form(
	form.Textbox("vURL", description="Video URL", size=41),
	form.Textbox("ecode", description="Event Code (ex. 2016arc)"),
	form.Textbox("mcode",description="Match Code (ex. qm1 or qfm5)",size=41))

class index:
	def GET(self):
		form = dataform()
		return render.forms(form)
	def POST(self):
		form = dataform()
		if not form.validates():
			return render.forms(form)
		vID = video_id(form.d.vURL)
		youtube = get_authenticated_service()
		update_description(youtube, vID, form.d.ecode, form.d.mcode)
		return render.forms(form)

if __name__=="__main__":
	web.internalerror = web.debugerror
	app.run()