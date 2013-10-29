#!/usr/bin/python
"""Script to interface with Plex to find old media that can be deleted"""

from optparse import OptionParser
import sys
import time
import urllib2
from xml.etree import ElementTree


def parse_options():
    """Parse command line options"""
    usage = "Usage: %prog [options] SERVER"
    parser = OptionParser(usage)
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      help='Turn on debugging')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        #FIXME: Show the actual usage here
        print(parser.get_usage())
        sys.exit(1)
    options.server = args[0]
    return options


class Plex:
    options = None
    sections = None
    section_keys = ['title']

    def __init__(self, options):
        """Class initialiser"""
        self.options = options
        self.urlbase = "http://%s:32400" % options.server

    def dbg(self, message):
        """Print a debugging statement"""
        if self.options.debug:
            print("DEBUG: %s" % message)

    def err(self, message):
        """Print an error statement"""
        print("ERROR: %s" % message)

    def trim_dict(self, source_dict, keys):
        """Return a filtered version of 'source_dict'"""
        new_dict = {new_key: source_dict[new_key]
                    for new_key in keys if new_key in source_dict}
        self.dbg(str(new_dict))
        return new_dict

    def fetch_tree(self, url):
        """Fetch the XML tree for a url"""
        self.dbg("Fetching: %s" % url)
        page = urllib2.urlopen(url)
        return ElementTree.parse(page)

    def find_sections(self):
        """Get the media sections"""
        self.sections = {}
        tree = self.fetch_tree("%s/library/sections" % self.urlbase)
        for section in tree.iter("Directory"):
            self.sections[section.attrib['type']] = \
                self.trim_dict(section.attrib, ['title', 'key'])

    def find_tv_shows(self):
        """Get the TV shows"""
        shows = {}
        tree = self.fetch_tree("%s/library/sections/%s/all" % (
                               self.urlbase, self.sections['show']['key']))
        for show in tree.iter("Directory"):
            shows[show.attrib['ratingKey']] = self.trim_dict(show.attrib,
                                                             ['title'])
        return shows

    def find_tv_seasons(self, show):
        """Get the seasons for a TV show"""
        seasons = {}
        tree = self.fetch_tree("%s/library/metadata/%s/children" % (
                               self.urlbase, show))
        for season in tree.iter("Directory"):
            if not "ratingKey" in season.attrib:
                continue
            seasons[season.attrib['ratingKey']] = self.trim_dict(season.attrib,
                                                                 ['title'])
        return seasons

    def find_tv_episodes(self, show, season):
        """Get the episodes for a season of a TV show"""
        episodes = {}
        tree = self.fetch_tree("%s/library/metadata/%s/children" % (
                               self.urlbase, season))

        for episode in tree.iter("Video"):
            data = self.get_tv_episode(episode.attrib['ratingKey'])
            episodes[episode.attrib['ratingKey']] = \
                self.trim_dict(data, ['title', 'ratingKey', 'viewCount',
                                      'lastViewedAt'])
        return episodes

    def get_tv_episode(self, episode_id):
        """Get the metadata for a specific TV episode"""
        tree = self.fetch_tree("%s/library/metadata/%s" % (
                               self.urlbase, episode_id))
        episode = tree.find("Video")
        return episode.attrib

    def get_watched_tv_episodes(self, max_age):
        """Get TV episodes that were watched more than 'age' seconds ago"""
        watched_episodes = []

        self.find_sections()
        shows = self.find_tv_shows()
        for show_id in shows.keys():
            show = shows[show_id]
            shows[show_id]['seasons'] = self.find_tv_seasons(show_id)
            for season_id in shows[show_id]['seasons'].keys():
                season = show['seasons'][season_id]
                season['episodes'] = self.find_tv_episodes(show_id, season_id)
                for episode_id in season['episodes'].keys():
                    episode = season['episodes'][episode_id]
                    if not "viewCount" in episode or \
                       not "lastViewedAt" in episode or \
                       int(episode["viewCount"]) <= 0:
                        self.dbg("Skipping %s::%s::%s. Not watched" % (
                                 show["title"], season["title"],
                                 episode["title"]))
                        continue
                    age = int(time.time()) - int(episode["lastViewedAt"])
                    if age > max_age:
                        self.dbg("Marking %s::%s::%s for expiry" % (
                                 show["title"], season["title"],
                                 episode["title"]))
                        watched_episodes.append({"show": show["title"],
                                                 "season": season["title"],
                                                 "episode": episode})
                    else:
                        self.dbg("Skipping %s::%s::%s from expiry" % (
                                 show["title"], season["title"],
                                 episode["title"]))
        return watched_episodes

    def delete(self, media_id):
        """Delete a specific piece of media"""
        url = ("%s/library/metadata/%s" % (self.urlbase, media_id))
        self.dbg("Deleting: %s" % media_id)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.get_method = lambda: 'DELETE'
        url = opener.open(request)


def main():
    options = parse_options()
    plex = Plex(options)

    month_old_tv = plex.get_watched_tv_episodes(30*24*60*60)
    for episode in month_old_tv:
        print "Deleting: %s, %s, %s" % (episode['show'], episode['season'],
                                        episode['episode']['title'])
        #        plex.delete(episode['episode']['ratingKey'])

#   three_month_old_movies = plex.get_watched_movies(90*24*60*60)
#   for movie in three_month_old_movies:
#       plex.delete(movie)

if __name__ == "__main__":
    main()
