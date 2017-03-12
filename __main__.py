import start, addTBAToDescription, addtoplaylist, TBA, tbaAPI, updatePlaylistThumbnails, updateThumbnail, \
    youtubeAuthenticate, youtubeup, socket


def internet(host="www.google.com", port=80, timeout=4):
    try:
    	host = socket.gethostbyname(host)
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as e:
        print "No internet!"
        return False


if internet():
	start.main()
