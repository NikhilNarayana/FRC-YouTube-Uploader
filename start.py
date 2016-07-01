import web
from web import form
import youtubeup as yup
import argparse

render = web.template.render('webpage/')

urls = ('/', 'index')
app = web.application(urls, globals())

dataform = form.Form(
    form.Textbox("ename", description="Event Name"),
    form.Textbox("ecode", description="Event Code (ex. 2016arc)"),
    form.Textbox("pID",
        form.regexp("^PL", "Must be a playlist ID"),
        description="Playlist ID"),
    form.Textbox("tbaID", description="TBA Event ID"),
    form.Textbox("tbaSecret", description="TBA Event Secret"),
    form.Textbox("mnum",
    	form.notnull,
    	form.regexp("\d+", "Must be a digit"),
    	form.Validator("Must be more than 0", lambda x:int(x)>0),
        description="Match Number"),
    form.Dropdown("mcode",
        ["qm", "qf", "sf", "f"],
        description="Match Type"),
    form.Textbox("end", description="Last Match Number"))

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
            yup.init(args)
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
            form.d.mnum = str(int(form.d.mnum) + 1)
            return render.forms(form)

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()