#!/usr/bin/env python3

from sys import platform, argv, exit

import pyforms_lite

from . import consts
from .forms import *
from .youtube import *
from .updateTBA import main as utmain
from .playlistToTBA import main as pttmain
from .updatePlaylistThumbnails import main as uptmain


def main():
    consts.youtube = get_youtube_service()
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
    try:
        pyforms_lite.start_app(FRC_Uploader, geometry=(200, 200, 1, 1))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
