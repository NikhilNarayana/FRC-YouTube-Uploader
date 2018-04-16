#!/usr/bin/env python3

import os
import csv
import sys
import socket
import threading
from time import sleep

import youtubeAuthenticate as YA
import youtubeup as yup


from PyQt5 import QtCore
from datetime import datetime
import pyforms
from argparse import Namespace
from pyforms import BaseWidget
from pyforms.controls import ControlText
from pyforms.controls import ControlTextArea
from pyforms.controls import ControlCombo
from pyforms.controls import ControlButton, ControlCheckBox


class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass


class FRC_Uploader(BaseWidget):

    def __init__(self):
        super(FRC_Uploader, self).__init__("FRC YouTube Uploader")
        # Redirct print output
        sys.stdout = EmittingStream(textWritten=self.writePrint)
        # Create form fields
        self._topbutton = ControlButton('Submit')
        # Event Values
        self._where = ControlCombo("Match Files Location")
        self._prodteam = ControlText("Production Team")
        self._twit = ControlText("Twitter Handle")
        self._fb = ControlText("Facebook Name")
        self._weblink = ControlText("Website Link")
        self._ename = ControlText("Event Name")
        self._ecode = ControlText("Event Code")
        self._pID = ControlText("Playlist ID")
        self._tbaID = ControlText("TBA ID")
        self._tbaSecret = ControlText("TBA Secret")
        self._description = ControlTextArea("Video Description")
        # Match Values
        self._mcode = ControlText("Match Code")
        self._mnum = ControlText("Match Number")
        self._mtype = ControlCombo("Match Type")
        self._tiebreak = ControlCheckBox("Tiebreaker")
        self._tba = ControlCheckBox("Use TBA")
        self._ceremonies = ControlCombo("Ceremonies")
        self._eday = ControlCombo("Event Day")
        self._end = ControlText("Last Match Number")

        # Output Box
        self._output = ControlTextArea()
        self._output.readonly = True
        self._output.autoscroll = True

        self.formset = [{"-Match Values": ["_mcode", "_mnum", "_mtype", "=", "_tiebreak", "||", "_tba", "=", "_ceremonies", "_eday", "_end"],
                         "-Status Output-": ["_output"],
                         "Event Values-": ["_where", "=", "_prodteam", "||", "_twit", "||", "_fb", "=", "_weblink", "||", "_ename", "||", "_ecode", "=", "_pID", "||", "_tbaID", "||", "_tbaSecret", "=", "_description"]},
                        '=', (' ', '_button', ' ')]

        self._button = ControlButton('Submit')

        # Set TBA check
        self._tba.value = True

        # Set Default Text
        self._tbaID.value += "Go to thebluealliance.com/request/apiwrite to get keys"
        self._tbaSecret.value += "Go to thebluealliance.com/request/apiwrite to get keys"
        self._description.value += "Add alternate description here."
        self._mcode.value += "0"
        self._mnum.value += "1"
        self._end.value += "Only for batch uploads"

        # Add ControlCombo values
        self._where += ("Parent Folder", "../")
        self._where += ("Same Folder", "")
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
        self._button.value = self.__buttonAction
        self._topbutton.value = self.__buttonAction

        # Get latest values from form_values.csv
        try:
            with open('form_values.csv') as csvfile:
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
                            else:
                                switcher[i].value = val
                        i = i + 1
                    break
        except (IOError, OSError, StopIteration) as e:
            print("No form_values.csv to read from, continuing with default values")

    def __buttonAction(self):
        """Button action event"""
        thra = threading.Thread(target=self.testprint)
        thra.daemon = True
        thra.start()
        # then = datetime.now()
        # options = Namespace()
        # row = None
        # try:
        #     reader = csv.reader(open('form_values.csv'))
        #     row = next(reader)
        # except (StopIteration, IOError, OSError) as e:
        #     with open("form_values.csv", "w+") as csvf:  # if the file doesn't exist
        #         csvf.write(''.join(str(x) for x in [","] * 18))
        #         reader = csv.reader(open("form_values.csv"))
        #         row = next(reader)
        # options.then = then
        # options.where = row[0] = self._where.value
        # options.prodteam = row[1] = self._prodteam.value
        # options.twit = row[2] = self._twit.value
        # options.fb = row[3] = self._fb.value
        # options.weblink = row[4] = self._weblink.value
        # options.ename = row[5] = self._ename.value
        # options.ecode = row[6] = self._ecode.value
        # options.pID = row[7] = self._pID.value
        # options.tbaID = row[8] = self._tbaID.value
        # options.tbaSecret = row[9] = self._tbaSecret.value
        # options.description = row[10] = self._description.value
        # options.mcode = row[11] = self._mcode.value
        # options.mnum = row[12] = int(self._mnum.value)
        # options.mtype = row[13] = self._mtype.value
        # options.tiebreak, row[14] = (True, "yes") if self._tiebreak.value else (False, "no")
        # options.tba, row[15] = (True, "yes") if self._tba.value else (False, "no")
        # options.ceremonies = row[16] = self._ceremonies.value
        # options.eday = row[17] = self._eday.value
        # options.end = row[18] = self._end.value
        # thr = threading.Thread(target=yup.init, args=(options,))
        # thr.daemon = True
        # thr.start()
        # if int(self._ceremonies.value) == 0:
        #     if self._end.value == "Only for batch uploads":
        #         self._mnum.value = str(int(self._mnum.value) + 1)
        #     else:
        #         self._mnum.value = str(int(self._end.value) + 1)
        #         self._end.value = "Only for batch uploads"
        # elif int(self._ceremonies.value) == 2:
        #     self._mnum.value = "1"
        #     self._mtype.value = "qf"
        # if self._mtype.value == "qm" and self._tiebreak.value:
        #     self._tiebreak.value = False
        # row[12] = int(self._mnum.value)
        # row[18] = self._end.value
        # writer = csv.writer(open('form_values.csv', 'w'))
        # writer.writerow(row)

    def writePrint(self, text):
        self._output.value += text
        print(text, file=sys.__stdout__, end= '')

    def testprint(self):
        for i in range(1000):
            print(i)
            sleep(.25)


def internet(host="www.google.com", port=80, timeout=4):
    try:
        host = socket.gethostbyname(host)
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True
    except Exception as e:
        print(e)
        print("No internet!")
        return False


def main():
    if "linux" in sys.platform:  # root needed for writing files
        if os.geteuid() != 0:
            print("Need sudo for writing files")
            subprocess.call(['sudo', 'python', sys.argv[0]])
    YA.get_youtube_service()
    YA.get_spreadsheet_service()
    if internet():
        pyforms.start_app(FRC_Uploader, geometry=(0, 0, 400, 550))
    else:
        return


if __name__ == "__main__":
    main()
