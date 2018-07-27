#!/usr/bin/env python3

from sys import platform, argv, exit
import socket

import pyforms_lite

from .forms import *
from .updateTBA import main as utmain
from .playlistToTBA import main as pttmain
from .updatePlaylistThumbnails import main as uptmain


def internet(host="www.google.com", port=80, timeout=4):
    """
    Quick way to check if you are connected to the internet by connecting to google
    """
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
    if len(argv) > 1:
        if "-p" in argv:
            pttmain()
            exit(0)
        elif "-u" in argv:
            utmain()
            exit(0)
        elif "-t" in argv:
            uptmain()
            exit(0)
        else:
            print("Not a valid option")
            print("Valid options include [-p|-u|-t]")
            print("-p will load playlistToTBA")
            print("-u will load updateTBA")
            print("-t will load updatePlaylistThumbnails")
            exit(0)
    if "linux" in platform:  # root needed for writing files
        from os import geteuid
        if geteuid():
            print("Need sudo for writing files")
            subprocess.call(['sudo', 'python3', argv[0]])
    if internet():
        try:
            pyforms_lite.start_app(
                FRC_Uploader, geometry=(100, 100, 1, 1))  # smallest size
        except Exception as e:
            print(e)
    else:
        return


if __name__ == "__main__":
    main()
