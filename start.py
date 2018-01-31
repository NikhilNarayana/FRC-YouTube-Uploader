#!/usr/bin/env python3

import os
import csv
import sys
import time
import socket
import threading
import subprocess

import uploaderSysUI
from time import sleep
import youtubeup as yup
from datetime import datetime
from argparse import Namespace
import youtubeAuthenticate as YA

def internet(host="www.google.com", port=80, timeout=4):
    try:
        host = socket.gethostbyname(host)
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        print("No internet!")
        return False


def sys_ui(app):
    uploader_form = QWidget()
    ui_builder = uploaderSysUI.Ui_uploader_form()
    ui_builder.setupUi(uploader_form)
    ui_builder.submit.clicked.connect(lambda: upload(ui_builder))
    uploader_form.show()
    sys.exit(app.exec_())


def upload(options):
    WIDGET_DATA_FUNCTIONS = {
        'QComboBox': 'currentText',
        'QPlainTextEdit': 'toPlainText'
    }
    data = dict()
    widgets = vars(options)
    for widget in widgets:
        if issubclass(type(widgets[widget]), QWidget):
            widget_type = re.search(
                '(?<=PyQt5\.QtWidgets\.)\w+', str(type(widgets[widget])))
            widget_type = widget_type.group() if widget_type else ''
            if widget_type in WIDGET_DATA_FUNCTIONS:
                data[widget] = getattr(
                    widgets[widget], WIDGET_DATA_FUNCTIONS[widget_type])()

    for key in data:
        print('%s: %s' % (key, data[key]))


def main():
    app = QApplication(list())
    if "linux" in sys.platform:  # root needed for writing files
        if os.geteuid() != 0:
            print("Need sudo for writing files")
            subprocess.call(['sudo', 'python', sys.argv[0]])
    YA.get_youtube_service()
    YA.get_spreadsheet_service()
    if internet():
        sys_ui(app)
        while True:
            try:
                sleep(100)
            except KeyboardInterrupt:
                print("\nQuitting Program")
                return
    else:
        return


if __name__ == "__main__":
    main()
