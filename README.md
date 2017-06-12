Plexpiry queries a Plex media server to find Movies and/or TV shows that meet
specified criteria, and deletes them.

```
Usage: plexpiry.py [options]

Options:
  -h, --help            show this help message and exit
  -d, --debug           turn on debugging
  -n, --dry-run         simulate run and display what would be removed
  -s SERVER, --server=SERVER
                        server to talk to [default: localhost]
  -p PORT, --port=PORT  port to talk to the server on [default 32400]

  -c FILE, --config=FILE config file to read
```

Config file format:

The config file is INI style. There are several global sections you can use:
 * global
 * movies
 * tv

Each of these sections can contain the following keys:
 * watched
 * unwatched
 * aired
 * ignore

For the first three of these keys (watched, unwatched, aired), the value should be a time specification that indicates the age of media to delete. This can be a number of seconds, or a number followed by 'd', 'w' or 'y' to indicate that the number means days, weeks or years, respectively.

The final key (ignore) should have a boolean value indicating whether or not the matching media should be ignored entirely.

Additionally, you can also have keys for the names of media (i.e. either movie titles, or TV show titles).

A complex example config might look like this:

    [global]
    unwatched = 180d
    watched = 90d

    [movie]
    watched = 30d

    [tv]
    aired = 365d

    [Movie 2:The Reckoning]
    ignore = True

    [Daily TV Show]
    watched = 1d
    unwatched = 7d

This will delete any watched movie after 30 days, any unwatched movie or TV show after 180d, and any watched TV show after 90 days, except for Movie 2: The Reckoning which will be kept forever, and Daily TV Show, which will be deleted after 1 day if watched, or 7 days if unwatched.

Simple :)
