#!/usr/bin/env python

import os
import csv
import web
import sys
import time
import socket
import threading
import webbrowser
import subprocess

import argparse
from web import form
from time import sleep
import youtubeup as yup
from datetime import datetime
import youtubeAuthenticate as YA

render = web.template.render('webpage/')

dataform = form.Form(
	form.Dropdown("where",
		[("../","Parent Folder to Scripts"),("", "Same Folder as Scripts")],
		description="Match Files Location"),
	form.Textbox("prodteam", description="Production Team", size=41),
	form.Textbox("twit", 
		form.Validator("Remove @", lambda x: x[0] != "@"),
		description="Twitter Handle", size=41),
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
	form.Textbox("mcode",
		form.Validator("Must be 0 if not used properly", lambda x: any(k in x for k in ("qm","qf","sf","f1m","0")) or x == ""),
		value="0",
		description="Match Code"),
	form.Textbox("mnum",
		form.notnull,
		form.regexp("\d+", "Cannot contain letters"),
		form.Validator("Must be more than 0", lambda x: int(x)>0),
		description="Match Number"),
	form.Dropdown("mtype",
		[("qm", "Qualifications"), ("qf","Quarterfinals"), ("sf", "Semifinals"), ("f1m", "Finals")],
		description="Match Type"),
	form.Dropdown("tiebreak",[("no","False"),("yes","True")],description="Tiebreaker"),
	form.Dropdown("tba",[("yes","True"),("no","False")],description="Update TBA"),
	form.Dropdown("ceremonies",[(0,"None"),(1,"Opening Ceremonies"),(2,"Alliance Selection"),(3,"Closing Ceremonies")],description="Ceremonies"),
	form.Dropdown("eday",[(0,"Ignore"),(1,"1"),(2,"2"),(3,"3")], description="Event Day"),
	form.Textbox("end",
		description="Last Match Number", 
		value="Only for batch uploads"),
	validators = [form.Validator("Last Match Number must be greater than Match Number", 
		lambda i: i.end == "Only for batch uploads" or int(i.end) > int(i.mnum))]
	)

class index(threading.Thread):
	def run(self):
		urls = ('/', 'index')
		app = web.application(urls, globals())
		webbrowser.open_new("http://localhost:8080")
		app.run()

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
							11: myform.mcode,
							12: myform.mnum,
							13: myform.mtype,
							14: myform.tiebreak,
							15: myform.tba,
							16: myform.ceremonies,
							17: myform.eday,
							18: myform.end,
						}
						switcher[i].set_value(value)
					i = i + 1
				break
		return render.forms(myform)

	def POST(self):
		then = datetime.now() #tracking for the time delta
		myform = dataform()
		if not myform.validates():
			return render.forms(myform)
		else:
			reader = csv.reader(open('form_values.csv'))
			try:
				row = next(reader)
			except StopIteration:
				with open("form_values.csv", "wb") as csvf: #if the file doesn't exist
					csvf.write(''.join(str(x) for x in [","]*30))
					csvf.close()
					row = next(reader)
			if "thebluealliance" in myform.d.mcode:
				myform.mcode.set_value(myform.d.mcode.split("_")[-1])
			args = argparse.ArgumentParser().parse_args()
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
			args.mcode = row[11] = myform.d.mcode
			args.mnum = row[12] = int(myform.d.mnum)
			args.mtype = row[13] = myform.d.mtype
			args.tiebreak = 0 if myform.d.tiebreak == "no" else 1
			row[14] = myform.d.tiebreak
			args.tba = 0 if myform.d.tba == "no" else 1
			row[15] = myform.d.tba
			args.ceremonies = row[16] = myform.d.ceremonies
			args.eday = row[17] = myform.d.eday
			args.end = row[18] = myform.d.end
			thr = threading.Thread(target=yup.init, args=(args,))
			thr.daemon = True
			thr.start()
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
			row[12] = int(myform.d.mnum)
			row[18] = myform.d.end
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
	if os.geteuid() != 0 and "linux" in sys.platform: #root needed for writing files
		print("Need root for writing files")
		subprocess.call(['sudo', 'python', sys.argv[0]])
	YA.get_youtube_service()
	YA.get_spreadsheet_service()
	web.internalerror = web.debugerror
	if internet():
		t = index()
		t.daemon = True
		t.start()
		while True:
			try:
				sleep(100)
			except KeyboardInterrupt:
				print "\nQuitting Program"
				return
	else:
		return

if __name__=="__main__":
	main()
