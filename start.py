#!/usr/bin/env python

import web
from web import form
import youtubeup as yup
import argparse
import csv
from datetime import datetime
import time
import sys
import socket

render = web.template.render('webpage/')

urls = ('/', 'index')
app = web.application(urls, globals())

dataform = form.Form(
	form.Dropdown("where",
		[("../","Parent Folder to Scripts"),("", "Same Folder as Scripts")],
		description="Match Files Location"),
	form.Textbox("prodteam", description="Production Team", size=41),
	form.Textbox("twit", description="Twitter Handle", size=41),
	form.Textbox("fb", description="Facebook Name", size=41),
	form.Textbox("weblink", description="Website Link", size=41),
	form.Textbox("ename", description="Event Name", size=41),
	form.Textbox("ecode", description="Event Code (ex. 2016arc)"),
	form.Textbox("pID",
		form.regexp("^PL", "Must be a playlist ID, all of which start with 'PL'"),
		form.regexp("^\s*\S+\s*$", "Can not contain spaces."),
		description="Playlist ID",
		size=41),
	form.Textbox("tbaID",
		description="TBA Event ID",
		value="Go to thebluealliance.com/request/apiwrite to get keys",
		size=41),
	form.Textbox("tbaSecret",
		description="TBA Event Secret",
		value="Go to thebluealliance.com/request/apiwrite to get keys",
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
		[("qm", "Qualifications"), ("qf","Quarterfinals"), ("sf", "Semifinals"), ("f1m", "Finals")],
		description="Match Type"),
	form.Dropdown("tiebreak",[("no","False"),("yes","True")],description="Tiebreaker"),
        form.Dropdown("tba",[("yes","True"),("no","False")],description="Update TBA"),
        form.Dropdown("ceremonies",[(0,"None"),(1,"Opening Ceremonies"),(2,"Alliance Selection"),(3,"Closing Ceremonies")],description="Ceremonies"),
	form.Textbox("end", 
		description="Last Match Number", 
		value="Only for batch uploads"),
		validators = [form.Validator("Last Match Number must be greater than Match Number", 
		lambda i: i.end == "Only for batch uploads" or int(i.end) > int(i.mnum))]
	)

class index():
	def GET(self):
		myform = dataform()
		with open('form_values.csv', 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='|')
			i = 0
			for row in reader:
				for value in row:
					if value is not "":
						switcher = {
							0: myform.where,
							1: myform.prodteam,
							2: myform.twit,
							3: myform.fb,
							4: myform.weblink,
							5: myform.ename,
							6: myform.ecode,
							7: myform.pID,
							8: myform.tbaID,
							9: myform.tbaSecret,
							10: myform.description,
							11: myform.mnum,
							12: myform.mcode,
							13: myform.tiebreak,
							14: myform.tba,
							15: myform.ceremonies,
							16: myform.end,
						}
						switcher[i].set_value(value)
					i = i + 1
				break
		return render.forms(myform)

	def POST(self):
		myform = dataform()
		if not myform.validates():
			return render.forms(myform)
		else:
			then = datetime.now()
			reader = csv.reader(open('form_values.csv'))
			try:
				row = next(reader)
			except StopIteration:
				with open("form_values.csv", "wb") as csvf:
					csvf.write(''.join(str(x) for x in [","]*30))
					csvf.close()
					row = next(reader)
			parser = argparse.ArgumentParser(description='Upload videos to YouTube for FRC matches')
			args = parser.parse_args()
			formdata = web.input()
			args.then = then
			args.gui = True
			args.where = row[0] = myform.d.where
			args.prodteam = row[1] = myform.d.prodteam
			args.twit = row[2] = myform.d.twit
			args.fb = row[3] = myform.d.fb
			args.weblink = row[4] = myform.d.weblink
			args.ename = row[5] = myform.d.ename
			args.ecode = row[6] = myform.d.ecode
			args.pID = row[7] = myform.d.pID
			args.tbaID = row[8] = myform.d.tbaID
			args.tbaSecret = row[9] = myform.d.tbaSecret
			args.description = row[10] = myform.d.description
			args.mnum = row[11] = int(myform.d.mnum)
			args.mcode = row[12] = myform.d.mcode
			args.tiebreak = 0 if myform.d.tiebreak == "no" else 1
			row[13] = myform.d.tiebreak
			args.tba = 0 if myform.d.tba == "no" else 1
			row[14] = myform.d.tba
			args.ceremonies = row[15] = myform.d.ceremonies
			args.end = row[16] = myform.d.end
			yup.init(args)
			if int(myform.d.ceremonies) == 0:
				if myform.d.end == "Only for batch uploads":
					myform.mnum.set_value(str(int(myform.d.mnum) + 1))
				else:
					myform.mnum.set_value(str(int(myform.d.end) + 1))
					myform.end.set_value("Only for batch uploads")
			elif int(myform.d.ceremonies) == 2:
				myform.mnum.set_value("1")
				myform.mcode.set_value("qf")
			if myform.d.mcode == "qm" and myform.d.tiebreak == "yes":
				myform.tiebreak.set_value("no")
			row[11] = int(myform.d.mnum)
			row[16] = myform.d.end
			writer = csv.writer(open('form_values.csv', 'w'))
			writer.writerow(row)
			return render.forms(myform)

def internet(host="www.google.com", port=80, timeout=4):
    try:
    	host = socket.gethostbyname(host)
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        print "No internet!"
        return False
			
def main():
	web.internalerror = web.debugerror
	if internet():
		app.run()
	else:
		return

if __name__=="__main__":
	main()
