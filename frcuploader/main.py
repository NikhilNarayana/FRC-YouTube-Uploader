#!/usr/bin/env python3

from os import geteuid
from sys import platform, argv
import socket

import pyforms

from .forms import *
from . import youtubeAuthenticate as YA


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
    if "linux" in platform:  # root needed for writing files
        if geteuid() != 0:
            print("Need sudo for writing files")
            subprocess.call(['sudo', 'python3', argv[0]])
    YA.get_youtube_service()
    YA.get_spreadsheet_service()
    if internet():
        pyforms.start_app(FRC_Uploader, geometry=(100, 100, 1, 1))  # 1, 1 shrinks it to the smallest possible size
    else:
        return


if __name__ == "__main__":
    main()
