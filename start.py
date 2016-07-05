import web
from web import form
import youtubeup as yup
import argparse

render = web.template.render('webpage/')

urls = ('/', 'index')
app = web.application(urls, globals())

dataform = form.Form(
	form.Textbox("ename", description="Event Name", size=41),
	form.Textbox("ecode", description="Event Code (ex. 2016arc)"),
	form.Textbox("pID",
		form.regexp("^PL", "Must be a playlist ID, all of which start with 'PL'"),
		form.regexp("^\s*\S+\s*$", "Can not contain spaces."),
		description="Playlist ID",
		size=41),
	form.Textbox("tbaID",
		description="TBA Event ID",
		value="Contact 'contact@thebluealliance.com to get keys",
		size=41),
	form.Textbox("tbaSecret",
		description="TBA Event Secret",
		value="Contact 'contact@thebluealliance.com to get keys",
		size=41),
	form.Textarea("description",
		description="Video description",
		value="Add alternate description here."),
	form.Textbox("mnum",
		form.notnull,
		form.regexp("\d+", "Cannot contain letters"),
		form.Validator("Must be more than 0", lambda x:int(x)>0),
		description="Match Number"),
	form.Dropdown("mcode",
		["qm", "qf", "sf", "f"],
		description="Match Type"),
	form.Checkbox("tiebreak", description="Tiebreaker"),
	form.Textbox("end", 
		description="Last Match Number", 
		value="Only for batch uploads"),
	validators = [form.Validator("Last Match Number must be greater than Match Number", 
		lambda i: i.end == "Only for batch uploads" or int(i.end) > int(i.mnum))]
	)

class index:
	def GET(self):
		form = dataform()
		return render.forms(form)

	def POST(self):
		form = dataform()
		if not form.validates():
			return render.forms(form)
		else:
			parser = argparse.ArgumentParser(description='Upload videos to YouTube for FRC matches')
			args = parser.parse_args()
			args.gui = True
			args.mnum = int(form.d.mnum)
			args.mcode = form.d.mcode
			args.pID = form.d.pID
			args.ename = form.d.ename
			args.ecode = form.d.ecode
			args.tbaID = form.d.tbaID
			args.tbaSecret = form.d.tbaSecret
			args.description = form.d.description
			args.tiebreak = form.d.tiebreak
			yup.init(args)
			if form.d.end == "Only for batch uploads":
				form.mnum.set_value(str(int(form.d.mnum) + 1))
			else:
				form.mnum.set_value(str(int(form.d.end) + 1))
				form.end.set_value("Only for batch uploads")
			return render.forms(form)

if __name__=="__main__":
	web.internalerror = web.debugerror
	app.run()