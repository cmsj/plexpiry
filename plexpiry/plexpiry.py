#!/usr/bin/python
"""Script to interface with Plex to find old media that can be deleted."""

import sys
import time
import urllib2
from xml.etree import ElementTree
from optparse import OptionParser, OptionGroup


def parse_options():
    """Parse command line options."""
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      help='turn on debugging')
    parser.add_option('-n', '--dry-run', action='store_true', dest='dryrun',
                      help='simulate run and display what would be removed')
    parser.add_option('-s', '--server', action='store', dest='server',
                      default='localhost',
                      help='server to talk to [default: %default]')
    parser.add_option('-p', '--port', action='store', dest='port',
                      default='32400',
                      help='port to talk to the server on [default %default]')

    group = OptionGroup(parser, "Expiry options",
                        "These options let you configure what kinds of media "
                        "you want to expire, and when. "
                        "Times default to seconds, but you can specify "
                        "d, w, y suffixes for days/weeks/years "
                        "respectively")
    group.add_option('--watched-tv', action='store',
                     dest='watched_tv', metavar='TIME',
                     help='expire watched TV shows after TIME')
    group.add_option('--unwatched-tv', action='store',
                     dest='unwatched_tv', metavar='TIME',
                     help='expire unwatched TV shows after TIME')
    group.add_option('--watched-movies', action='store',
                     dest='watched_movies', metavar='TIME',
                     help='expire watched movies after TIME')
    group.add_option('--unwatched-movies', action='store',
                     dest='unwatched_movies', metavar='TIME',
                     help='expire unwatched movies after TIME')
    parser.add_option_group(group)

    group = OptionGroup(parser, "Ignore options",
                        "These options let you ignore movies and TV shows "
                        "that you do not want to ever be expired."
                        "They can be specified multiple times.")
    group.add_option('--ignore-tv-show', action='append',
                     dest='ignore_tv_shows', default='',
                     metavar='SHOW',
                     help='a TV show to ignore')
    group.add_option('--ignore-movie', action='append',
                     dest='ignore_movies', default='',
                     metavar='MOVIE',
                     help='a movie to ignore')
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    if None == options.watched_tv == options.unwatched_tv == \
       options.watched_movies == options.unwatched_movies:
        print("Error: You must specify at least one expiry option")
        parser.print_help()
        sys.exit(1)
    return options


class Plexpiry:
    options = None
    sections = None

    def __init__(self, options):
        self.options = options
        self.dbg(self.options)
        self.urlbase = "http://%s:%s" % (options.server, options.port)

    def dbg(self, message):
        """Print a debugging statement."""
        if self.options.debug:
            print("DEBUG: %s" % message)

    def err(self, message):
        """Print an error statement."""
        print("ERROR: %s" % message)

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
        try:
            return int(time)
        except ValueError:
            period = time[-1:]
            if period in ['d', 'D']:
                return int(time[:-1]) * 86400
            elif period in ['w', 'W']:
                return int(time[:-1]) * 86400 * 7
            elif period in ['y', 'Y']:
                return int(time[:-1]) * 86400 * 365
            else:
                raise ValueError("Unable to parse: %s" % time)

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
                                      'lastViewedAt', 'addedAt'])
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
                                      'lastViewedAt', 'addedAt'])
        return movies

    def get_watched_tv_episodes(self, max_age):
        """Get TV episodes that were watched more than 'max_age' seconds ago.
        """
        watched_episodes = []

        shows = self.get_tv_tree()

        for show_id in shows:
            show = shows[show_id]
            for season_id in shows[show_id]['seasons']:
                season = shows[show_id]['seasons'][season_id]
                for episode_id in season['episodes']:
                    episode = season['episodes'][episode_id]
                    msg = "Inspecting %s:%s:%s: " % (show["title"],
                                                     season["title"],
                                                     episode["title"])

                    if "lastViewedAt" not in episode:
                        self.dbg("%s Skipping. Not watched" % msg)
                        continue

                    age = int(time.time()) - int(episode["lastViewedAt"])

                    if age < max_age:
                        self.dbg("%s Skipping. Not old enough" % msg)
                        continue
                    else:
                        self.dbg("%s Expiring." % msg)
                        watched_episodes.append({"show": show["title"],
                                                 "season": season["title"],
                                                 "episode": episode})

        return watched_episodes

    def get_unwatched_tv_episodes(self, max_age):
        """Get TV episodes that have not been watched, and were added more than
        'max_age' seconds ago.
        """
        unwatched_episodes = []

        shows = self.get_tv_tree()

        for show_id in shows:
            show = shows[show_id]
            for season_id in shows[show_id]['seasons']:
                season = shows[show_id]['seasons'][season_id]
                for episode_id in season['episodes']:
                    episode = season['episodes'][episode_id]
                    msg = "Inspecting %s:%s:%s: " % (show["title"],
                                                     season["title"],
                                                     episode["title"])

                    if "lastViewedAt" in episode:
                        self.dbg("%s Skipping. Watched" % msg)
                        continue

                    age = int(time.time()) - int(episode["addedAt"])

                    if age < max_age:
                        self.dbg("%s Skipping. Not old enough" % msg)
                        continue
                    else:
                        self.dbg("%s Expiring." % msg)
                        unwatched_episodes.append({"show": show["title"],
                                                   "season": season["title"],
                                                   "episode": episode})

        return unwatched_episodes

    def get_watched_movies(self, max_age):
        """Get movies that have been watched more than 'max_age' seconds
        ago.
        """
        watched_movies = []

        movies = self.get_movie_tree()

        for movie_id in movies:
            movie = movies[movie_id]
            msg = "Inspecting %s" % movie["title"]

            if "lastViewedAt" not in movie:
                self.dbg("%s Skipping. Not watched" % msg)
                continue

            age = int(time.time()) - int(movie["lastViewedAt"])

            if age < max_age:
                self.dbg("%s Skipping. Not old enough" % msg)
                continue
            else:
                self.dbg("%s Expiring. " % msg)
                watched_movies.append(movie)

        return watched_movies

    def get_unwatched_movies(self, max_age):
        """Get movies that have not been watched and were added more than
        'max_age' seconds ago
        """
        unwatched_movies = []

        movies = self.get_movie_tree()

        for movie_id in movies:
            movie = movies[movie_id]
            msg = "Inspecting %s" % movie["title"]

            if "lastViewedAt" in movie:
                self.dbg("%s Skipping. Watched" % msg)
                continue

            age = int(time.time()) - int(movie["addedAt"])

            if age < max_age:
                self.dbg("%s Skipping. Not old enough" % msg)
                continue
            else:
                self.dbg("%s Expiring." % msg)
                unwatched_movies.append(movie)

        return unwatched_movies

    def delete(self, media_id):
        """Delete a specific piece of media."""
        url = ("%s/library/metadata/%s" % (self.urlbase, media_id))
        self.dbg("Deleting: %s" % media_id)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.get_method = lambda: 'DELETE'
        if not self.options.dryrun:
            url = opener.open(request)


def main():
    options = parse_options()
    plex = Plexpiry(options)

    if options.watched_tv:
        time = plex.parse_time(options.watched_tv)
        episodes = plex.get_watched_tv_episodes(time)
        for episode in episodes:
            plex.dbg("Deleting: %s:%s:%s" % (episode['show'],
                                             episode['season'],
                                             episode['episode']['title']))
            plex.delete(episode['episode']['ratingKey'])

    if options.unwatched_tv:
        time = plex.parse_time(options.unwatched_tv)
        episodes = plex.get_unwatched_tv_episodes(time)
        for episode in episodes:
            plex.dbg("Deleting: %s:%s:%s" % (episode['show'],
                                             episode['season'],
                                             episode['episode']['title']))
            plex.delete(episode['episode']['ratingKey'])

    if options.watched_movies:
        time = plex.parse_time(options.watched_movies)
        movies = plex.get_watched_movies(time)
        for movie in movies:
            plex.dbg("Deleting: %s" % movie['title'])
            plex.delete(movie['ratingKey'])

    if options.unwatched_movies:
        time = plex.parse_time(options.unwatched_movies)
        movies = plex.get_unwatched_movies(time)
        for movie in movies:
            plex.dbg("Deleting: %s" % movie['title'])
            plex.delete(movie['ratingKey'])


if __name__ == "__main__":
    main()
