#!/usr/bin/env python3

import os
import sys
import json
import pickle
import threading
import subprocess
from time import sleep
from queue import Queue
from copy import deepcopy
from datetime import datetime
from distutils.version import StrictVersion as sv

from . import consts
from . import utils

import requests
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
            latest_version = requests.get('https://pypi.org/pypi/FRCUploader/json').json()['info']['version']
            if sv(latest_version) > sv(consts.__version__):  # prevents messages when developing
                if "linux" in sys.platform:
                    self.message(f"Current Version: {consts.__version__}\nVersion {latest_version} is available.\n You can update with this command: pip3 install -U frcuploader=={latest_version}", title="FRCUploader")
                else:
                    resp = self.question(f"Current Version: {consts.__version__}\nVersion {latest_version} is available. Would you like to update?", title="FRCUploader")
                    if resp == "yes":
                        ret = subprocess.call(('pip3', 'install', '-U', f'frcuploader=={latest_version}'))
                        if ret:
                            self.message(f'The app failed to update\nType "pip3 install -U frcuploader=={latest_version}" into CMD/Terminal to update', title="FRCUploader")
                        else:
                            self.info("You can now restart the app to use the new version", title="FRCUploader")
        except Exception as e:
            print(e)
        super(FRC_Uploader, self).__init__(f"FRC YouTube Uploader - {consts.__version__}")

        # Redirct print output
        sys.stdout = EmittingStream(textWritten=self.write_print)

        # Redirect error output to window, console, and file
        sys.stderr = EmittingStream(textWritten=self.write_err)

        # Queue
        self._queue = Queue()
        self._queueref = []

        # Create form fields
        # Event Values
        self._where = ControlDir(" Match Files Location")
        self._newest = ControlCheckBox("Get Newest File")
        self._sendto = ControlDir(" Move Files To")
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
        self._replay = ControlCheckBox("Replay")
        self._ceremonies = ControlCombo("Ceremonies")
        self._eday = ControlCombo("Event Day")
        self._end = ControlNumber("Last Match Number", minimum=0, maximum=500)

        # Output Box
        self._output = ControlTextArea()
        self._output.readonly = True
        self._qview = ControlList("Queue", select_entire_row=True)
        self._qview.cell_double_clicked_event = self.__ignore_job
        self._qview.readonly = True
        self._qview.horizontal_headers = ["Event Code", "Match Type", "Match #"]

        # Button
        self._button = ControlButton('Submit')
        self._ascrollbutton = ControlButton("Toggle Scroll")
        self._autoscroll = True

        # Form Layout
        self.formset = [{
            "-Match Values":
            [(' ', "_mcode", ' '), (' ', "_mnum", ' '), (' ', "_mtype", ' '),
             (' ', "_tiebreak", "_tba", "_replay", ' '), (' ', "_ceremonies", ' '),
             (' ', "_eday", ' '), (' ', "_end", ' ')],
            "-Status Output-":
            ["_output", (' ', "_ascrollbutton", ' '), "=", "_qview"],
            "Event Values-": [("_where", "_newest"), "_sendto", ("_prodteam", "_twit", "_fb"),
                              ("_weblink", "_ename", "_ecode"),
                              ("_pID", "_tbaID", "_tbaSecret"), ("_privacy", " "), "_description"]
        }, (' ', '_button', ' ')]

        # Main Menu Layout
        self.mainmenu = [{
            'Settings': [{'Youtube Log Out': self.__reset_cred}, {'Show/Hide Match Code': self.__toggle_match_code}],
            'Save/Clear': [{'Save Form': self.__save_form}, {'Clear Form': self.__reset_form}],
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

        self._form_fields = (
            self._where,
            self._prodteam,
            self._twit,
            self._fb,
            self._weblink,
            self._ename,
            self._ecode,
            self._pID,
            self._tbaID,
            self._tbaSecret,
            self._description,
            self._mcode,
            self._mnum,
            self._mtype,
            self._tiebreak,
            self._tba,
            self._ceremonies,
            self._eday,
            self._end,
            self._newest,
            self._privacy,
            self._sendto,
        )
        self.__load_form()

    def __togglescroll(self):
        self._autoscroll = False if self._autoscroll else True

    def __button_action(self):
        """Manipulates and transforms data from the forms into usable
           data that can be used for uploading videos"""
        options = Namespace()
        options.where = self._where.value
        options.prodteam = self._prodteam.value
        options.twit = self._twit.value
        options.fb = self._fb.value
        options.weblink = self._weblink.value
        options.ename = self._ename.value
        options.ecode = self._ecode.value
        f = self._pID.value.find("PL")
        self._pID.value = self._pID.value[f:f + 34]
        options.pID = self._pID.value
        options.tbaID = self._tbaID.value
        options.tbaSecret = self._tbaSecret.value
        if not consts.trusted and options.tbaID and options.tbaSecret and options.ecode:
            consts.tba.update_trusted(options.tbaID, options.tbaSecret, options.ecode)
        options.description = self._description.value
        options.mcode = self._mcode.value
        options.mnum = int(self._mnum.value)
        options.mtype = self._mtype.value
        options.tiebreak = deepcopy(self._tiebreak.value)
        options.tba = deepcopy(self._tba.value)
        options.ceremonies = self._ceremonies.value
        options.eday = self._eday.value
        options.end = 0
        options.replay = self._replay.value
        self._replay.value = False
        options.newest = deepcopy(self._newest.value)
        if options.newest:
            files = list(reversed([f for f in os.listdir(options.where) if os.path.isfile(os.path.join(options.where, f)) and not f.startswith('.') and any(f.endswith(z) for z in consts.rec_formats)]))
            options.file = max([os.path.join(options.where, f) for f in files], key=os.path.getmtime)
            for f in files:
                if f in options.file:
                    options.filebasename = f
        options.privacy = self._privacy.value
        options.sendto = self._sendto.value
        options.ignore = False
        if not int(self._end.value):
            if options.ceremonies:
                self._qview += (options.ecode, consts.cerem[options.ceremonies], "N/A")
            else:
                self._qview += (options.ecode, options.mtype, options.mnum)
        elif not options.newest:
            for r in range(options.mnum, int(self._end.value)):
                self._qview += (options.ecode, options.mtype, options.mnum)
                self._queue.put(options)
                self._queueref.append(options)
                self._qview.resize_rows_contents()
                options = deepcopy(options)
                options.mnum += 1
        else:
            print("Using Last Match Number and Get Newest File together is not supported")
            print(f"Will fallback to just uploading the newest file for mnum {options.mnum}")
            self._end.value = 0
        if int(self._end.value):
            self._qview += (options.ecode, options.mtype, options.mnum)
        self._queue.put(options)
        self._queueref.append(options)
        self._qview.resize_rows_contents()
        if consts.first_run:
            thr = threading.Thread(target=self.__worker)
            thr.daemon = True
            thr.start()
            consts.first_run = False
        if not self._ceremonies.value:
            if not int(self._end.value):
                self._mnum.value = self._mnum.value + 1
            else:
                self._mnum.value = self._end.value + 1
                self._end.value = 0
        elif self._ceremonies.value == 2:
            self._mnum.value = 1
            self._mtype.value = "qf"
        if self._mtype.value == "qm" and self._tiebreak.value:
            self._tiebreak.value = False
        self.__save_form()

    def write_print(self, text):
        self._output._form.plainTextEdit.insertPlainText(text)
        if self._autoscroll:
            self._output._form.plainTextEdit.moveCursor(QtGui.QTextCursor.End)
        if sys.__stdout__:
            print(text, file=sys.__stdout__, end='')

    def write_err(self, text):
        self._output._form.plainTextEdit.insertPlainText(text)
        if self._autoscroll:
            self._output._form.plainTextEdit.moveCursor(QtGui.QTextCursor.End)
        if sys.__stdout__:
            print(text, file=sys.__stdout__, end='')
        with open(consts.log_file, "a") as f:
            f.write(text)

    def __worker(self):
        while not consts.stop_thread:
            options = self._queue.get()
            if not options.ignore:
                options.then = datetime.now()
                utils.init(options)
                self._qview -= 0
                self._queueref.pop(0)
            self._queue.task_done()
        else:
            print("Uploads are stopped")

    def __toggle_worker(self):
        if not consts.stop_thread:
            print("Stopping Uploads")
            consts.stop_thread = True
            consts.first_run = False
        else:
            print("Ready to Upload")
            consts.stop_thread = False
            consts.first_run = True

    def __save_form(self, options=[]):
        row = [None] * (len(self._form_fields) + 1)
        if options:
            f = options.pID.find("PL")
            options.pID = options.pID[f:f + 34]
            row[0] = deepcopy(options.where)
            row[1] = deepcopy(options.prodteam)
            row[2] = deepcopy(options.twit)
            row[3] = deepcopy(options.fb)
            row[4] = deepcopy(options.weblink)
            row[5] = deepcopy(options.ename)
            row[6] = deepcopy(options.ecode)
            row[7] = deepcopy(options.pID)
            row[8] = deepcopy(options.tbaID)
            row[9] = deepcopy(options.tbaSecret)
            row[10] = deepcopy(options.description)
            row[11] = deepcopy(options.mcode)
            row[12] = deepcopy(options.mnum)
            row[13] = deepcopy(options.mtype)
            row[14] = deepcopy(options.tiebreak)
            row[15] = deepcopy(options.tba)
            row[16] = deepcopy(options.ceremonies)
            row[17] = deepcopy(options.eday)
            row[18] = deepcopy(options.end)
            row[19] = deepcopy(options.newest)
            row[20] = deepcopy(options.privacy)
            row[21] = deepcopy(options.sendto)
        else:
            f = self._pID.value.find("PL")
            self._pID.value = self._pID.value[f:f + 34]
            for i, var in zip(range(len(self._form_fields) + 1), self._form_fields):
                row[i] = deepcopy(var.value)
        with open(consts.form_values, 'w') as f:
                f.write(json.dumps(row))
        return row

    def __load_form(self):
        try:
            with open(consts.form_values, "r") as f:
                values = json.loads(f.read())
                for val, var in zip(values, self._form_fields):
                    if isinstance(val, bool):
                        var.value = True if val else False
                    elif val:
                        var.value = val
        except (IOError, OSError, StopIteration, json.decoder.JSONDecodeError):
            print(f"No {consts.abbrv}_form_values.json to read from, continuing with default values")

    def __save_queue(self):
        if os.path.exists(consts.queue_values):
            resp = self.question(f"A queue already exists would you like to overwrite it?\nIt was last modified on {datetime.utcfromtimestamp(int(os.path.getmtime(consts.queue_values))).strftime('%Y-%m-%d')}")
            if resp == "yes":
                with open(consts.queue_values, "wb") as f:
                    f.write(pickle.dumps(self._queueref))
                print("Saved Queue, you can now close the program")
            elif resp == "no":
                resp = self.question("Would you like to add onto the end of that queue?")
                if resp == "yes":
                    queueref = None
                    with open(consts.queue_values, "rb") as f:
                        queueref = pickle.load(f)
                    queueref.extend(self._queueref)
                    with open(consts.queue_values, "wb") as f:
                        f.write(pickle.dumps(queueref))
                    print("Saved Queue, you can now close the program")
                else:
                    self.message("Not saving queue")

    def __load_queue(self):
        if self._queueref:
            resp = self.question("Would you like to add to the existing queue?\nItems will be added to the front of the queue.")
            if resp == "yes":
                try:
                    with open(consts.queue_values, "rb") as f:
                        queueref = pickle.load(f)
                    queueref.extend(self._queueref)
                    self._queueref = queueref
                    self._qview.clear()
                    self._qview.horizontal_headers = ["Event Code", "Match Type", "Match #"]
                    for options in self._queueref:
                        if options.ceremonies:
                            self._qview += (options.ecode, consts.cerem[options.ceremonies], "N/A")
                        else:
                            self._qview += (options.ecode, options.mtype, options.mnum)
                        self._queue.put(options)
                        self._qview.resize_rows_contents()
                        self.__save_form(options)
                except Exception:
                    print("You need to save a queue before loading a queue")
                    return
        else:
            try:
                with open(consts.queue_values, "rb") as f:
                    self._queueref = pickle.load(f)
                for options in self._queueref:
                    if options.ceremonies:
                        self._qview += (options.ecode, consts.cerem[options.ceremonies], "N/A")
                    else:
                        self._qview += (options.ecode, options.mtype, options.mnum)
                    self._queue.put(options)
                    self._qview.resize_rows_contents()
                    self.__save_form(options)
            except Exception:
                print("You need to save a queue before loading a queue")
                return

        resp = self.question("Do you want to start uploading?")
        if resp == "yes":
            thr = threading.Thread(target=self.__worker)
            thr.daemon = True
            consts.first_run = False
            consts.stop_thread = False
            thr.start()

    def __reset_form(self):
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
        self._sendto.value = ""
        self._prodteam.value = ""
        self._twit.value = ""
        self._fb.value = ""
        self._weblink.value = ""
        self._ename.value = ""
        self._ecode.value = ""
        self._pID.value = ""

    def __reset_cred(self):
        title = consts.youtube.channels().list(part='snippet', mine=True).execute()
        title = title['items'][0]['snippet']['title']
        resp = self.question(f"You are currently logged into {title}\nWould you like to log out?", title="FRCUploader")
        if resp == "yes":
            os.remove(os.path.join(consts.root, ".frc-oauth2-youtube.json"))
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
