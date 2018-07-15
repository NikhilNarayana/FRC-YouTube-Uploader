#!/usr/bin/env python3

from sys import platform, argv
import socket

import pyforms

from .forms import *


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
        from os import geteuid
        if geteuid():
            print("Need sudo for writing files")
            subprocess.call(['sudo', 'python3', argv[0]])
    if internet():
        try:
            pyforms.start_app(
                FRC_Uploader, geometry=(100, 100, 1, 1))  # smallest size
        except Exception as e:
            print(e)
    else:
        return


if __name__ == "__main__":
    main()
