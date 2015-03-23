#!/usr/bin/python
"""Script to interface with Plex to find media that can be deleted."""

import argparse
import ConfigParser
import copy
import datetime
import os
import sys
import time
import urllib2
from xml.etree import ElementTree

DEFAULT_CONFIG = {}


def parse_options(args=None):
    """Parse command line options."""
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description='Delete old media from Plex',
                                     formatter_class=formatter)
    parser.add_argument('-d', '--debug', action='store_true', dest='debug',
                        help='turn on debugging', default=False)
    parser.add_argument('-n', '--dry-run', action='store_true', dest='dryrun',
                        help='simulate run and display what would be removed',
                        default=False)
    parser.add_argument('-s', '--server', action='store', dest='server',
                        default='localhost',
                        help='server to talk to')
    parser.add_argument('-p', '--port', action='store', dest='port',
                        default='32400', type=int,
                        help='port to talk to')
    parser.add_argument('-c', '--config', action='store', dest='config_file',
                        default='~/.config/plexpiry.conf',
                        help='Configuration file')

    options = parser.parse_args(args)

    return options


class Plexpiry:
    options = None
    config = None
    sections = None
    has_deleted = False

    def __init__(self, options):
        self.options = options
        self.dbg("Command line options: %s" % self.options)
        self.urlbase = "http://%s:%s" % (options.server, options.port)
        self.load_config()

    def dbg(self, message):
        """Print a debugging statement."""
        if self.options.debug:
            try:
                print("DEBUG: %s" % message)
            except UnicodeEncodeError:
                print("Sorry, Python sucks at Unicode.")

    def err(self, message):
        """Print an error statement."""
        print("ERROR: %s" % message)

    def info(self, message):
        """Print an info statement."""
        print("INFO: %s" % message)

    def open_config_file(self):
        """Open the config file."""
        path = os.path.expanduser(self.options.config_file)
        fd = open(path)
        return fd

    def load_config(self):
        """Load the config file."""
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(self.open_config_file())

    def trim_dict(self, source_dict, keys):
        """Return a filtered version of 'source_dict'."""
        new_dict = {new_key: source_dict[new_key]
                    for new_key in keys if new_key in source_dict}
        self.dbg(str(new_dict))
        return new_dict

    def parse_time(self, time):
        """Return a number of seconds, based on the input
        which can end with d/w/y for days/weeks/years.
        """
        parsed_time = -1
        try:
            parsed_time = int(time)
        except ValueError:
            period = time[-1:]
            if period in ['d', 'D']:
                parsed_time = int(time[:-1]) * 86400
            elif period in ['w', 'W']:
                parsed_time = int(time[:-1]) * 86400 * 7
            elif period in ['y', 'Y']:
                parsed_time = int(time[:-1]) * 86400 * 365

        if parsed_time >= 0:
            return parsed_time
        else:
            raise ValueError("Unable to parse: %s" % time)

    def get_config_sections(self):
        """Get all the sections in the config."""
        return self.config.sections()

    def get_config_section(self, section):
        """Get a single section as a dict."""
        tmpconfig = {}
        try:
            items = self.config.items(section)
        except ConfigParser.NoSectionError:
            return None

        for (key, value) in items:
            tmpconfig[key] = value
        return tmpconfig

    def collapse_config(self, title, kind):
        """Construct a per-title configuration dict that takes global values
        and layers per-title values over the top
        """
        unionconfig = copy.deepcopy(DEFAULT_CONFIG)
        unionconfig["__name"] = title

        for section in ["global", kind, title]:
            tmp = self.get_config_section(section)
            if tmp:
                unionconfig.update(tmp)

        self.dbg("Resolved config for '%s' to: %s" % (title, unionconfig))
        return unionconfig

    def is_watched(self, media):
        """Determine if a piece of media has been watched."""
        return ("lastViewedAt" in media)

    def fetch_tree(self, url):
        """Fetch the XML tree for a url."""
        self.dbg("Fetching: %s" % url)
        return ElementTree.parse(urllib2.urlopen(url))

    def find_sections(self):
        """Get the media sections."""
        self.sections = {}
        tree = self.fetch_tree("%s/library/sections" % self.urlbase)
        for section in tree.iter("Directory"):
            self.sections[section.attrib['type']] = \
                self.trim_dict(section.attrib, ['title', 'key'])
        self.dbg("Found sections: %s" % self.sections)

    def refresh_plex(self):
        """Instruct Plex to re-index the library after we've done our work."""
        for section in [self.sections["movie"]["key"],
                        self.sections["show"]["key"]]:
            url = "%s/library/sections/%s/refresh" % (self.urlbase, section)
            self.dbg("Refreshing Plex at: %s" % url)
            if not self.options.dryrun:
                urllib2.urlopen(url)

    def find_tv_shows(self):
        """Get the TV shows."""
        shows = {}
        tree = self.fetch_tree("%s/library/sections/%s/all" % (
                               self.urlbase, self.sections['show']['key']))
        for show in tree.iter("Directory"):
            shows[show.attrib['ratingKey']] = self.trim_dict(show.attrib,
                                                             ['title'])
        return shows

    def find_tv_seasons(self, show):
        """Get the seasons for a TV show."""
        seasons = {}
        tree = self.fetch_tree("%s/library/metadata/%s/children" % (
                               self.urlbase, show))
        for season in tree.iter("Directory"):
            if "ratingKey" not in season.attrib:
                continue
            seasons[season.attrib['ratingKey']] = self.trim_dict(season.attrib,
                                                                 ['title'])
        return seasons

    def find_tv_episodes(self, show, season):
        """Get the episodes for a season of a TV show."""
        episodes = {}
        tree = self.fetch_tree("%s/library/metadata/%s/children" % (
                               self.urlbase, season))

        for episode in tree.iter("Video"):
            data = self.get_tv_episode(episode.attrib['ratingKey'])
            episodes[episode.attrib['ratingKey']] = \
                self.trim_dict(data, ['title', 'ratingKey', 'viewCount',
                                      'lastViewedAt', 'addedAt',
                                      'originallyAvailableAt'])
        return episodes

    def get_tv_episode(self, episode_id):
        """Get the metadata for a specific TV episode."""
        tree = self.fetch_tree("%s/library/metadata/%s" % (
                               self.urlbase, episode_id))
        episode = tree.find("Video")
        return episode.attrib

    def get_tv_tree(self):
        """Build a full tree of shows, seasons and episodes."""
        self.find_sections()
        shows = self.find_tv_shows()

        for show_id in shows:
            show = shows[show_id]
            shows[show_id]['seasons'] = self.find_tv_seasons(show_id)
            for season_id in shows[show_id]['seasons']:
                season = show['seasons'][season_id]
                season['episodes'] = self.find_tv_episodes(show_id, season_id)

        return shows

    def get_movie(self, movie_id):
        """Get the metadata for a specific movie."""
        tree = self.fetch_tree("%s/library/metadata/%s" % (
                               self.urlbase, movie_id))
        movie = tree.find("Video")
        return movie.attrib

    def get_movie_tree(self):
        """Build a full tree of movies."""
        self.find_sections()
        movies = {}
        tree = self.fetch_tree("%s/library/sections/%s/all" % (
                               self.urlbase, self.sections['movie']['key']))
        for movie in tree.iter("Video"):
            data = self.get_movie(movie.attrib['ratingKey'])
            movies[movie.attrib['ratingKey']] = \
                self.trim_dict(data, ['title', 'ratingKey', 'viewCount',
                                      'lastViewedAt', 'addedAt',
                                      'originallyAvailableAt'])
        return movies

    def should_expire_media(self, media, config):
        """Determine if a piece of mediais expired."""
        if "ignore" in config and config["ignore"]:
            self.dbg("Ignoring: '%s' per configuration" % config["__name"])
            return False

        to_delete = []
        keypairs = []
        is_watched = self.is_watched(media)

        if is_watched and "watched" in config:
            keypairs.append(("lastViewedAt", "watched"))
        if "aired" in config:
            keypairs.append(("originallyAvailableAt", "aired"))
        if not is_watched and "unwatched" in config:
            keypairs.append(("addedAt", "unwatched"))

        if len(keypairs) == 0:
            self.dbg("No configuration matches: %s" % config["__name"])
            return False

        for key, config_key in keypairs:
            age = self.get_media_age(media, key)
            configtime = self.parse_time(config[config_key])
            if age > configtime:
                to_delete.append(config_key)

        if len(to_delete) == 0:
            return False
        else:
            return to_delete

    def get_media_age(self, media, key):
        """Calculate the age of a piece of media, given some time value."""
        time_now = int(time.time())
        if key == "originallyAvailableAt":
            event = (datetime.datetime.strptime(media[key], "%Y-%m-%d") -
                     datetime.datetime(1970, 1, 1)).total_seconds()
        else:
            event = int(media[key])

        return (time_now - event)

    def delete(self, media_id):
        """Delete a specific piece of media."""
        self.has_deleted = True
        url = ("%s/library/metadata/%s" % (self.urlbase, media_id))
        self.dbg("Deleting: %s" % media_id)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.get_method = lambda: 'DELETE'
        if not self.options.dryrun:  # pragma: no cover
            url = opener.open(request)
        self.dbg("Making HTTP call: %s %s" % (request.get_method(),
                                              request.get_full_url()))

    def expire(self):
        """Process all media for being expired."""
        # First up, movies
        movies = self.get_movie_tree()
        for movie_id in movies:
            movie = movies[movie_id]
            config = self.collapse_config(movie["title"], "movies")
            result = self.should_expire_media(movie, config)
            if result:
                self.info("Expiring: %s (matched: %s)" % (movie["title"],
                                                          result))
                self.delete(movie['ratingKey'])
            else:
                self.dbg("Skipping: %s" % movie["title"])

        # Next, TV
        shows = self.get_tv_tree()

        for show_id in shows:
            show = shows[show_id]
            config = self.collapse_config(show["title"], "tv")
            for season_id in show['seasons']:
                season = show['seasons'][season_id]
                for episode_id in season['episodes']:
                    episode = season['episodes'][episode_id]
                    result = self.should_expire_media(episode, config)
                    if result:
                        self.info("Expiring: %s:%s:%s (matched: %s)" %
                                  (show["title"],
                                   season["title"],
                                   episode["title"],
                                   result))
                        self.delete(episode["ratingKey"])
                    else:
                        self.dbg("Skipping: %s:%s:%s" % (show["title"],
                                                         season["title"],
                                                         episode["title"]))
        if self.has_deleted:
            self.refresh_plex()


def main():  # pragma: no cover
    try:
        plex = Plexpiry(parse_options())
    except ConfigParser.ParsingError as e:
        print("Unable to parse config file: %s" % e.message)
        sys.exit(1)

    plex.expire()

if __name__ == "__main__":  # pragma: no cover
    main()
