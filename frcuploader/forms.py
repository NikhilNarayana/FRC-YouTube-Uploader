#!/usr/bin/env python3

import os
import csv
import sys
import threading
from time import sleep
from queue import Queue

from .consts import DEFAULT_DESCRIPTION, DEBUG, cerem
from . import youtubeup as yup

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
        super(FRC_Uploader, self).__init__("FRC YouTube Uploader")
        # Redirct print output
        sys.stdout = EmittingStream(textWritten=self.write_print)
        # Queue
        self._queue = Queue()
        self._queueref = []
        self._firstrun = True

        # Create form fields
        # Event Values
        self._where = ControlDir(" Match Files Location")
        self._prodteam = ControlText(" Production Team")
        self._twit = ControlText("Twitter Handle")
        self._fb = ControlText("Facebook Name")
        self._weblink = ControlText(" Website Link")
        self._ename = ControlText("Event Name")
        self._ecode = ControlText("Event Code")
        self._pID = ControlText(" Playlist ID")
        self._tbaID = ControlText("TBA ID")
        self._tbaSecret = ControlText("TBA Secret")
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
        self._end = ControlText("Last Match Number")

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
            "Event Values-": [("_where", ' '), ("_prodteam", "_twit", "_fb"),
                              ("_weblink", "_ename", "_ecode"),
                              ("_pID", "_tbaID", "_tbaSecret"), "_description"]
        }, (' ', '_button', ' ')]

        # Main Menu Layout
        self.mainmenu = [{
            'Settings': [{
                'Reset Form Values': self.__reset_form_event
            }, {
                'Remove Youtube Credentials': self.__reset_cred_event
            }, {'Show/Hide Match Code': self.__toggle_match_code}]
        }]

        # Set TBA check
        self._tba.value = True

        # Set Default Text
        self._tbaID.value = "Go to thebluealliance.com/request/apiwrite to get keys"
        self._tbaSecret.value = "Go to thebluealliance.com/request/apiwrite to get keys"
        self._description.value = DEFAULT_DESCRIPTION
        self._mcode.value = "0"
        self._mnum.value = 1
        self._end.value = "For batch uploads"

        # Add ControlCombo values
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

        # Hide Alternate Description Box
        # self._description.hide()
        # self._output.hide()
        self.testval = 0

        # Get latest values from form_values.csv
        try:
            with open(os.path.join(os.path.expanduser("~"), ".form_values.csv")) as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                i = 0
                for row in reader:
                    for val in row:
                        if val is not "":
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
                            }
                            if any(i == k for k in (14, 15)):
                                if val == "no":
                                    switcher[i].value = False
                                else:
                                    switcher[i].value = True
                            elif i == 12:
                                switcher[i].value = int(val)
                            else:
                                switcher[i].value = val
                        i = i + 1
                    break
        except (IOError, OSError, StopIteration) as e:
            print("No form_values.csv to read from, continuing with default values and creating file")
            with open(os.path.join(os.path.expanduser("~"), ".form_values.csv"), "w+") as csvf:  # if the file doesn't exist
                csvf.write(''.join(str(x) for x in [","] * 18))

    def __togglescroll(self):
        self._autoscroll = False if self._autoscroll else True

    def __button_action(self):
        """Button action event"""
        if DEBUG:
            if self._firstrun:
                thr = threading.Thread(target=self.__worker)
                thr.daemon = True
                thr.start()
                self._firstrun = False
            self._queue.put(str(self.testval))
            self._queueref.append(str(self.testval))
            self._qview += (self.testval, self.testval, self.testval, self.testval)
            self.testval += 1
            self._qview.resize_rows_contents()
        else:
            options = Namespace()
            reader = None
            try:
                reader = csv.reader(open(os.path.join(os.path.expanduser("~"), ".form_values.csv")))
            except (StopIteration, IOError, OSError) as e:
                with open(os.path.join(os.path.expanduser("~"), ".form_values.csv"), "w+") as csvf:  # if the file doesn't exist
                    csvf.write(''.join(str(x) for x in [","] * 18))
                reader = csv.reader(open(os.path.join(os.path.expanduser("~"), ".form_values.csv")))
            row = next(reader)
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
            if options.end == "For batch uploads":
                if options.ceremonies:
                    self._qview += (options.ecode, cerem[options.ceremonies])
                self._qview += (options.ecode, options.mtype, options.mnum)
            else:
                self._qview += (options.ecode, options.mtype, options.mnum, options.end)
            options.ignore = False
            self._queue.put(options)
            self._queueref.append(options)
            self._qview.resize_rows_contents()
            if self._firstrun:
                thr = threading.Thread(target=self.__worker)
                thr.daemon = True
                thr.start()
                self._firstrun = False
            if int(self._ceremonies.value) == 0:
                if self._end.value == "For batch uploads":
                    self._mnum.value = int(self._mnum.value) + 1
                else:
                    self._mnum.value = int(self._end.value) + 1
                    self._end.value = "For batch uploads"
            elif int(self._ceremonies.value) == 2:
                self._mnum.value = 1
                self._mtype.value = "qf"
            if self._mtype.value == "qm" and self._tiebreak.value:
                row[14] = self._tiebreak.value = False
            row[12] = int(self._mnum.value)
            row[18] = self._end.value
            writer = csv.writer(open(os.path.join(os.path.expanduser("~"), ".form_values.csv"), 'w'))
            writer.writerow(row)

    def write_print(self, text):
        self._output._form.plainTextEdit.insertPlainText(text)
        if self._autoscroll:
            self._output._form.plainTextEdit.moveCursor(QtGui.QTextCursor.End)
        print(text, file=sys.__stdout__, end='')

    def __worker(self):
        if DEBUG:
            while True:
                val = self._queue.get()
                if val in self._queueref:
                    self._qview -= 0
                    print(val)
                    sleep(2)
                    self._queueref.pop(0)
                self._queue.task_done()
        else:
            while True:
                options = self._queue.get()
                if not options.ignore:
                    options.then = datetime.now()
                    yup.init(options)
                    self._qview -= 0
                    self._queueref.pop(0)
                self._queue.task_done()

    def __reset_form_event(self):
        with open(os.path.join(os.path.expanduser("~"), ".form_values.csv"), "w+") as csvf:
            csvf.write(''.join(str(x) for x in [","] * 18))
        self._tbaID.value = "Go to thebluealliance.com/request/apiwrite to get keys"
        self._tbaSecret.value = "Go to thebluealliance.com/request/apiwrite to get keys"
        self._description.value = DEFAULT_DESCRIPTION
        self._mcode.value = "0"
        self._mnum.value = 1
        self._end.value = "For batch uploads"
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
        os.remove(os.path.join(os.path.expanduser("~"), ".oauth2-spreadsheet.json"))
        os.remove(os.path.join(os.path.expanduser("~"), ".oauth2-youtube.json"))
        sys.exit(0)

    def __reset_descrip_event(self):
        self._description.value = DEFAULT_DESCRIPTION

    def __ignore_job(self, row, column):
        self._qview -= row
        if not DEBUG:
            self._queueref[row + 1].ignore = True
        self._queueref.pop(row + 1)

    def __toggle_match_code(self):
        if self._mcode.visible: 
            self._mcode.hide()
        else:
            self._mcode.show()
