#!/usr/bin/env python

import web
from web import form
import youtubeup as yup
import argparse
import csv
from datetime import datetime

render = web.template.render('webpage/')

urls = ('/', 'index')
app = web.application(urls, globals())

dataform = form.Form(
	form.Textbox("prodteam", description="Production Team", size=41),
	form.Textbox("twit", description="Twitter Handle", size=41),
	form.Textbox("fb", description="Facebook Name", size=41),
	form.Textbox("web", description="Website Link", size=41),
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
		[("qm", "Qualifications"), ("qf","Quarterfinals"), ("sf", "Semifinals"), ("f", "Finals")],
		description="Match Type"),
	form.Checkbox("tiebreak", description="Tiebreaker"),
	form.Checkbox("tba", checked=True, description="Use The Blue Alliance"),
	form.Textbox("end", 
		description="Last Match Number", 
		value="Only for batch uploads"),
		validators = [form.Validator("Last Match Number must be greater than Match Number", 
		lambda i: i.end == "Only for batch uploads" or int(i.end) > int(i.mnum))]
	)

class index:
	def GET(self):
		form = dataform()
		with open('form_values.csv', 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='|')
			i = 0
			for row in reader:
				for value in row:
					if value is not "":
						switcher = {
							0: form.prodteam,
							1: form.twit,
							2: form.fb,
							3: form.web,
							4: form.ename,
							5: form.ecode,
							6: form.pID,
							7: form.tbaID,
							8: form.tbaSecret,
							9: form.description,
							10: form.mnum,
							11: form.mcode,
							12: form.tiebreak,
							13: form.tba,
							14: form.end,
						}
						if i == 12 or i == 13:
							if value == "True": switcher[i].set_value(True)
							if value == "False": switcher[i].set_value(False)
						else : switcher[i].set_value(value)
					i = i + 1
				break
		return render.forms(form)

	def POST(self):
		form = dataform()
		if not form.validates():
			return render.forms(form)
		else:
			args.then = datetime.now()
			reader = csv.reader(open('form_values.csv'))
			row = next(reader)
			parser = argparse.ArgumentParser(description='Upload videos to YouTube for FRC matches')
			args = parser.parse_args()
			formdata = web.input()
			args.gui = True
			args.prodteam = row[0] = form.d.prodteam
			args.twit = row[1] = form.d.twit
			args.fb = row[2] = form.d.fb
			args.web = row[3] = form.d.web
			args.ename = row[4] = form.d.ename
			args.ecode = row[5] = form.d.ecode
			args.pID = row[6] = form.d.pID
			args.tbaID = row[7] = form.d.tbaID
			args.tbaSecret = row[8] = form.d.tbaSecret
			args.description = row[9] = form.d.description
			args.mnum = row[10] = int(form.d.mnum)
			args.mcode = row[11] = form.d.mcode
			args.tiebreak, row[12] = formdata.has_key('tiebreak'), str(formdata.has_key('tiebreak'))
			args.tba, row[13] = formdata.has_key('tba'), str(formdata.has_key('tba'))
			args.end = row[14] = form.d.end
			yup.init(args)
			if form.d.end == "Only for batch uploads":
				form.mnum.set_value(str(int(form.d.mnum) + 1))
			else:
				form.mnum.set_value(str(int(form.d.end) + 1))
				form.end.set_value("Only for batch uploads")
			row[6] = int(form.d.mnum)
			row[10] = form.d.end
			writer = csv.writer(open('form_values.csv', 'w'))
			writer.writerow(row)
			return render.forms(form)

if __name__=="__main__":
	web.internalerror = web.debugerror
	app.run()