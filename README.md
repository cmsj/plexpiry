Plexpiry queries a Plex media server to find Movies and/or TV shows that meet
specified criteria, and deletes them.

Usage: plexpiry.py [options]

Options:
  -h, --help            show this help message and exit
  -d, --debug           turn on debugging
  -n, --dry-run         simulate run and display what would be removed
  -s SERVER, --server=SERVER
                        server to talk to [default: localhost]
  -p PORT, --port=PORT  port to talk to the server on [default 32400]

  Expiry options:
    These options let you configure what kinds of media you want to
    expire, and when. Times default to seconds, but you can specify d, w,
    y suffixes for days/weeks/years respectively

    --watched-tv=TIME   expire watched TV shows after TIME
    --unwatched-tv=TIME
                        expire unwatched TV shows after TIME
    --watched-movies=TIME
                        expire watched movies after TIME
    --unwatched-movies=TIME
                        expire unwatched movies after TIME

  Ignore options:
    These options let you ignore movies and TV shows that you do not want
    to ever be expired.They can be specified multiple times.

    --ignore-tv-show=SHOW
                        a TV show to ignore
    --ignore-movie=MOVIE
                        a movie to ignore
