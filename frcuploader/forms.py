#!/usr/bin/env python3

import os
import sys
import json
import pickle
import threading
from time import sleep
from queue import Queue

from . import consts
from . import utils

import requests
from datetime import datetime
from argparse import Namespace

from pyforms_lite import BaseWidget
from PyQt5 import QtCore, QtGui
from pyforms_lite.controls import ControlNumber
from pyforms_lite.controls import ControlText, ControlDir
from pyforms_lite.controls import ControlTextArea, ControlList
from pyforms_lite.controls import ControlCombo, ControlProgress
from pyforms_lite.controls import ControlButton, ControlCheckBox


class EmittingStream(QtCore.QObject):
    """
    Capture any uses of print so it can be printed to a custom text box
    """
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass


class FRC_Uploader(BaseWidget):
    """
    GUI constructor.
    Create the GUI using pyforms_lite.start_app(FRC_Uploader)
    """

    def __init__(self):
        try:  # check if the user can update the app
            latest_version = requests.get('https://pypi.python.org/pypi/frcuploader/json').json()['info']['version']
            if (consts.__version__ != latest_version):
                if "linux" in sys.platform:
                    self.message(f"Current Version: {consts.__version__}\nVersion {latest_version} is available.\n You can update with this command: pip3 install -U frcuploader=={latest_version}", title="FRCUploader")
                else:
                    resp = self.question(f"Current Version: {consts.__version__}\nVersion {latest_version} is available. Would you like to update?", title="FRCUploader")
                    if resp == "yes":
                        subprocess.call(('pip3', 'install', '-U', f'frcuploader=={latest_version}'))
                        self.message("You can now restart the app to use the new version", title="FRCUploader")
        except Exception as e:
            print(e)
        super(FRC_Uploader, self).__init__("FRC YouTube Uploader")

        # Redirct print output
        sys.stdout = EmittingStream(textWritten=self.write_print)

        # Queue
        self._queue = Queue()
        self._queueref = []

        # Redirect error output to a file
        if not sys.stderr:
            sys.stderr = open(consts.log_file, "a")

        # Create form fields
        # Event Values
        self._where = ControlDir(" Match Files Location")
        self._newest = ControlCheckBox("Get Newest File")
        self._prodteam = ControlText(" Production Team")
        self._twit = ControlText("Twitter Handle")
        self._fb = ControlText("Facebook Name")
        self._weblink = ControlText(" Website Link")
        self._ename = ControlText("Event Name")
        self._ecode = ControlText("Event Code")
        self._pID = ControlText(" Playlist ID")
        self._tbaID = ControlText("TBA ID")
        self._tbaSecret = ControlText("TBA Secret")
        self._privacy = ControlCombo("Video Privacy Status")
        self._description = ControlTextArea(" Video Description")
        self._description.add_popup_menu_option("Reset", self.__reset_descrip_event)

        # Match Values
        self._mcode = ControlText("Match Code", visible=False, helptext="READ THE INSTRUCTIONS TO FIND OUT HOW TO USE THIS!")
        self._mnum = ControlNumber("Match Number", minimum=1, maximum=500)
        self._mtype = ControlCombo("Match Type")
        self._tiebreak = ControlCheckBox("Tiebreaker")
        self._tba = ControlCheckBox("Use TBA")
        self._ceremonies = ControlCombo("Ceremonies")
        self._eday = ControlCombo("Event Day")
        self._end = ControlNumber("Last Match Number", minimum=0, maximum=500)

        # Output Box
        self._output = ControlTextArea()
        self._output.readonly = True
        self._qview = ControlList("Queue", select_entire_row=True)
        self._qview.cell_double_clicked_event = self.__ignore_job
        self._qview.readonly = True
        self._qview.horizontal_headers = ["Event Code", "Match Type", "Match #", "Last Match #"]

        # Button
        self._button = ControlButton('Submit')
        self._ascrollbutton = ControlButton("Toggle Scroll")
        self._autoscroll = True

        # Form Layout
        self.formset = [{
            "-Match Values":
            [(' ', "_mcode", ' '), (' ', "_mnum", ' '), (' ', "_mtype", ' '),
             (' ', "_tiebreak", "_tba", ' '), (' ', "_ceremonies", ' '),
             (' ', "_eday", ' '), (' ', "_end", ' ')],
            "-Status Output-":
            ["_output", (' ', "_ascrollbutton", ' '), "=", "_qview"],
            "Event Values-": [("_where", "_newest"), ("_prodteam", "_twit", "_fb"),
                              ("_weblink", "_ename", "_ecode"),
                              ("_pID", "_tbaID", "_tbaSecret"), ("_privacy", " "), "_description"]
        }, (' ', '_button', ' ')]

        # Main Menu Layout
        self.mainmenu = [{
            'Settings': [{'Reset Form Values': self.__reset_form_event}, {'Youtube Log Out': self.__reset_cred_event}, {'Show/Hide Match Code': self.__toggle_match_code}],
            'Queue': [{'Toggle Uploads': self.__toggle_worker}, {'Save Queue': self.__save_queue}, {'Load Queue': self.__load_queue}]}]

        # Set TBA check
        self._tba.value = True

        # Set Default Text
        self._tbaID.value = "Go to thebluealliance.com/request/apiwrite to get keys"
        self._tbaSecret.value = "Go to thebluealliance.com/request/apiwrite to get keys"
        self._description.value = consts.DEFAULT_DESCRIPTION
        self._mcode.value = "0"
        self._mnum.value = 1

        # Add ControlCombo values
        for t in consts.VALID_PRIVACY_STATUSES:
            self._privacy += t
        self._mtype += ("Qualifications", "qm")
        self._mtype += ("Quarterfinals", "qf")
        self._mtype += ("Semifinals", "sf")
        self._mtype += ("Finals", "f1m")
        self._ceremonies += ("None", 0)
        self._ceremonies += ("Opening Ceremonies", 1)
        self._ceremonies += ("Alliance Selection", 2)
        self._ceremonies += ("Closing Ceremonies", 3)
        self._ceremonies += ("Highlight Reel", 4)
        self._eday += ("Ignore", 0)
        self._eday += ("1", 1)
        self._eday += ("2", 2)
        self._eday += ("3", 3)

        # Define the button action
        self._button.value = self.__button_action
        self._ascrollbutton.value = self.__togglescroll

        self.testval = 0

        # Get latest values from frc_form_values.json
        try:
            with open(consts.form_values) as f:
                values = json.load(f)
                i = 0
                switcher = {
                    0: self._where,
                    1: self._prodteam,
                    2: self._twit,
                    3: self._fb,
                    4: self._weblink,
                    5: self._ename,
                    6: self._ecode,
                    7: self._pID,
                    8: self._tbaID,
                    9: self._tbaSecret,
                    10: self._description,
                    11: self._mcode,
                    12: self._mnum,
                    13: self._mtype,
                    14: self._tiebreak,
                    15: self._tba,
                    16: self._ceremonies,
                    17: self._eday,
                    18: self._end,
                    19: self._newest,
                    20: self._privacy,
                }
                for val in values:
                    if i > 19:
                        break
                    if val is not "":
                        if any(i == k for k in (14, 15, 19)):
                            if val == "no":
                                switcher[i].value = False
                            else:
                                switcher[i].value = True
                        elif i == 12 or i == 18:
                            try:
                                switcher[i].value = int(val)
                            except Exception as e:
                                pass
                        else:
                            switcher[i].value = val
                    i = i + 1
        except (IOError, OSError, StopIteration) as e:
            print("No frc_form_values.json to read from, continuing with default values and creating file")
            with open(consts.form_values, "w+") as f:  # if the file doesn't exist
                f.write(json.dumps([]))

    def __togglescroll(self):
        self._autoscroll = False if self._autoscroll else True

    def __button_action(self):
        """Manipulates and transforms data from the forms into usable
           data that can be used for uploading videos"""
        options = Namespace()
        row = [0] * 21
        options.where = row[0] = self._where.value
        options.prodteam = row[1] = self._prodteam.value
        options.twit = row[2] = self._twit.value
        options.fb = row[3] = self._fb.value
        options.weblink = row[4] = self._weblink.value
        options.ename = row[5] = self._ename.value
        options.ecode = row[6] = self._ecode.value
        f = self._pID.value.find("PL")
        self._pID.value = self._pID.value[f:f + 34]
        options.pID = row[7] = self._pID.value
        options.tbaID = row[8] = self._tbaID.value
        options.tbaSecret = row[9] = self._tbaSecret.value
        options.description = row[10] = self._description.value
        options.mcode = row[11] = self._mcode.value
        options.mnum = row[12] = int(self._mnum.value)
        options.mtype = row[13] = self._mtype.value
        options.tiebreak, row[14] = (True, "yes") if self._tiebreak.value else (False, "no")
        options.tba, row[15] = (True, "yes") if self._tba.value else (False, "no")
        options.ceremonies = row[16] = self._ceremonies.value
        options.eday = row[17] = self._eday.value
        options.end = row[18] = self._end.value
        options.newest, row[19] = (True, "yes") if self._newest.value else (False, "no")
        options.privacy = row[20] = self._privacy.value
        options.ignore = False
        if not options.end:
            if options.ceremonies:
                self._qview += (options.ecode, consts.cerem[options.ceremonies], "N/A", "N/A")
            else:
                self._qview += (options.ecode, options.mtype, options.mnum, "N/A")
        else:
            self._qview += (options.ecode, options.mtype, options.mnum, options.end)
        self._queue.put(options)
        self._queueref.append(options)
        self._qview.resize_rows_contents()
        if consts.firstrun:
            thr = threading.Thread(target=self.__worker)
            thr.daemon = True
            thr.start()
            consts.firstrun = False
        if not self._ceremonies.value:
            if not self._end.value:
                self._mnum.value = int(self._mnum.value) + 1
            else:
                self._mnum.value = self._end.value + 1
                self._end.value = 0
        elif self._ceremonies.value == 2:
            self._mnum.value = 1
            self._mtype.value = "qf"
        if self._mtype.value == "qm" and self._tiebreak.value:
            row[14] = self._tiebreak.value = False
        row[12] = self._mnum.value
        row[18] = self._end.value
        with open(consts.form_values, 'w') as f:
            f.write(json.dumps(row))

    def write_print(self, text):
        self._output._form.plainTextEdit.insertPlainText(text)
        if self._autoscroll:
            self._output._form.plainTextEdit.moveCursor(QtGui.QTextCursor.End)
        print(text, file=sys.__stdout__, end='')

    def __worker(self):
        while True:
            options = self._queue.get()
            if not options.ignore:
                options.then = datetime.now()
                utils.init(options)
                self._qview -= 0
                self._queueref.pop(0)
            self._queue.task_done()

    def __toggle_worker(self):
        if not consts.stop_thread:
            print("Stopping Uploads")
            consts.stop_thread = True
            consts.firstrun = False
        else:
            print("Ready to Upload")
            consts.stop_thread = False
            consts.firstrun = True

    def __save_queue(self):
        with open(consts.queue_values, "wb") as f:
            f.write(pickle.dumps(self._queueref))

    def __load_queue(self):
        try:
            with open(consts.queue_values, "rb") as f:
                self._queueref = pickle.load(f)
        except Exception as e:
            print("You need to save a queue before loading a queue")
            return
        for options in self._queueref:
            if not options.end:
                if options.ceremonies:
                    self._qview += (options.ecode, consts.cerem[options.ceremonies], "N/A", "N/A")
                else:
                    self._qview += (options.ecode, options.mtype, options.mnum, "N/A")
            else:
                self._qview += (options.ecode, options.mtype, options.mnum, options.end)
            self._queue.put(options)
            self._qview.resize_rows_contents()
        thr = threading.Thread(target=self.__worker)
        thr.daemon = True
        consts.firstrun = False
        consts.stop_thread = False
        thr.start()

    def __reset_form_event(self):
        with open(consts.form_values, "w+") as f:
            f.write(json.dumps([]))
        self._tbaID.value = "Go to thebluealliance.com/request/apiwrite to get keys"
        self._tbaSecret.value = "Go to thebluealliance.com/request/apiwrite to get keys"
        self._description.value = consts.DEFAULT_DESCRIPTION
        self._mcode.value = "0"
        self._mnum.value = 1
        self._end.value = 0
        self._mtype.value = "qm"
        self._ceremonies.value = 0
        self._eday.value = 0
        self._tba.value = True
        self._where.value = ""
        self._prodteam.value = ""
        self._twit.value = ""
        self._fb.value = ""
        self._weblink.value = ""
        self._ename.value = ""
        self._ecode.value = ""
        self._pID.value = ""

    def __reset_cred_event(self):
        title = consts.youtube.channels().list(part='snippet', mine=True).execute()
        title = title['items'][0]['snippet']['title']
        resp = self.question(f"You are currently logged into {title}\nWould you like to log out?", title="FRCUploader")
        if resp == "yes":
            os.remove(os.path.join(os.path.expanduser("~"), ".frc-oauth2-spreadsheet.json"))
            os.remove(os.path.join(os.path.expanduser("~"), ".frc-oauth2-youtube.json"))
            sys.exit(0)

    def __reset_descrip_event(self):
        self._description.value = consts.DEFAULT_DESCRIPTION

    def __ignore_job(self, row, column):
        self._qview -= row
        self._queueref[row].ignore = True
        self._queueref.pop(row)

    def __toggle_match_code(self):
        if self._mcode.visible:
            self._mcode.hide()
        else:
            self._mcode.show()
