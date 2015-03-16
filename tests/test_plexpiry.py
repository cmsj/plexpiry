import fixtures
import os
import StringIO
import testtools
import urlparse

from plexpiry import plexpiry


FAKE_DICT = {'a': 1,
             'b': 2,
             'c': 3,
             'd': 4,
             }

# FIXME: Check this against a real response
FAKE_SECTIONS = {'show': {'key': '2', 'title': 'TV Shows'},
                 'movie': {'key': '1', 'title': 'Movies'},
                 }
FAKE_TV_SHOWS = {'425': {'title': 'Spaced'}}
FAKE_TV_SEASONS = {'426': {'title': 'Season 1'}, '434': {'title': 'Season 2'}}
FAKE_TV_EPISODES = {'433': {'addedAt': '1401322741',
                            'lastViewedAt': '1401322997',
                            'originallyAvailableAt': '2007-05-21',
                            'ratingKey': '433',
                            'title': 'Episode 7',
                            'viewCount': '1'}}
FAKE_TV_EPISODE = {'addedAt': '1401322741',
                   'art': '/library/metadata/425/art/1401322765',
                   'contentRating': 'Caution',
                   'duration': '1491000',
                   'grandparentKey': '/library/metadata/425',
                   'grandparentRatingKey': '425',
                   'grandparentTheme':
                   '/library/metadata/425/theme/1401322765',
                   'grandparentThumb':
                   '/library/metadata/425/thumb/1401322765',
                   'grandparentTitle': 'Spaced',
                   'guid': 'com.plexapp.agents.thetvdb://72658/1/7?lang=en',
                   'index': '7',
                   'key': '/library/metadata/433',
                   'lastViewedAt': '1401322997',
                   'originallyAvailableAt': '2007-05-21',
                   'parentIndex': '1',
                   'parentKey': '/library/metadata/426',
                   'parentRatingKey': '426',
                   'parentThumb': '/library/metadata/426/thumb/1401322765',
                   'rating': '8.3',
                   'ratingKey': '433',
                   'summary': "Daisy and Tim's domestic bliss is threatened "
                               "when Tim's ex-girlfriend reappears and wants "
                               "to get back together with him. Adult themes "
                               "and strong language",
                   'thumb': '/library/metadata/433/thumb/1401322765',
                   'title': 'Episode 7',
                   'type': 'episode',
                   'updatedAt': '1401322765',
                   'viewCount': '1',
                   'year': '2007'}
FAKE_MOVIES = {'1024': {'addedAt': '1418348404',
                        'lastViewedAt': '1418653256',
                        'originallyAvailableAt': '2013-09-02',
                        'ratingKey': '1024',
                        'title': 'The Zero Theorem',
                        'viewCount': '1'},
               '1135': {'addedAt': '1421060244',
                        'lastViewedAt': '1421675051',
                        'originallyAvailableAt': '2014-08-16',
                        'ratingKey': '1135',
                        'title': 'Zodiac: Signs of the Apocalypse',
                        'viewCount': '1'}}
FAKE_MOVIE_ONE = {'addedAt': '1418348404',
                  'art': '/library/metadata/1024/art/1418349807',
                  'chapterSource': 'media',
                  'contentRating': '15+',
                  'duration': '6387304',
                  'guid': 'com.plexapp.agents.imdb://tt2333804?lang=en',
                  'key': '/library/metadata/1024',
                  'lastViewedAt': '1418653256',
                  'originallyAvailableAt': '2013-09-02',
                  'rating': '5.9',
                  'ratingKey': '1024',
                  'studio': 'Picture Perfect Corporation',
                  'summary': "A computer hacker's goal to discover the reason "
                              "for human existence continually finds his work "
                              "interrupted thanks to the Management; this time"
                              ", they send a teenager and lusty love interest "
                              "to distract him.",
                  'tagline': 'Nothing is Everything',
                  'thumb': '/library/metadata/1024/thumb/1418349807',
                  'title': 'The Zero Theorem',
                  'titleSort': 'Zero Theorem',
                  'type': 'movie',
                  'updatedAt': '1418349807',
                  'viewCount': '1',
                  'year': '2013'}
FAKE_PATH = os.path.dirname(__file__)
FAKE_SECTIONS_XML = os.path.join(FAKE_PATH, "fake_sections.xml")
FAKE_SECTION_2_XML = os.path.join(FAKE_PATH, "fake_section_2.xml")
FAKE_TV_SHOWS_XML = os.path.join(FAKE_PATH, "fake_tv_shows.xml")
FAKE_TV_SEASONS_XML = os.path.join(FAKE_PATH, "fake_tv_seasons.xml")
FAKE_TV_EPISODES_XML = os.path.join(FAKE_PATH, "fake_tv_episodes.xml")
FAKE_TV_EPISODE_XML = os.path.join(FAKE_PATH, "fake_tv_episode.xml")
FAKE_TV_EPISODE_METADATA_XML = os.path.join(FAKE_PATH,
                                            "fake_tv_episode_metadata.xml")
FAKE_TV_EPISODE_2448_XML = os.path.join(FAKE_PATH, "2448.xml")
FAKE_TV_EPISODE_2254_XML = os.path.join(FAKE_PATH, "2254.xml")
FAKE_TV_EPISODE_2257_XML = os.path.join(FAKE_PATH, "2257.xml")
FAKE_TV_EPISODE_433_XML = os.path.join(FAKE_PATH, "433.xml")
FAKE_MOVIES_XML = os.path.join(FAKE_PATH, "fake_movies.xml")
FAKE_MOVIE_ONE_XML = os.path.join(FAKE_PATH, "fake_movie_one.xml")
FAKE_MOVIE_TWO_XML = os.path.join(FAKE_PATH, "fake_movie_two.xml")

TEST_TV_SHOW = 425
TEST_TV_SEASON = 426
TEST_TV_EPISODE = 433
TEST_MOVIE = 1024

FAKE_CONFIG_FILE = """[global]
unwatched = 180d
watched = 90d

[movies]
watched = 30d

[tv]
aired = 365d

[Octonauts]
ignore = True
"""


class FakeOptions():
    debug = False
    server = "fakeserver"
    port = "fakeport"


class TestPlexpiry(testtools.TestCase):

    def setUp(self):
        super(TestPlexpiry, self).setUp()

        def fake_urlopen(url):
            url = urlparse.urlparse(url)
            if url.path == "/library/sections":
                return open(FAKE_SECTIONS_XML)
            if url.path == "/library/sections/1/all":
                return open(FAKE_MOVIES_XML)
            if url.path == "/library/sections/2/all":
                return open(FAKE_TV_SHOWS_XML)
            if url.path == "/library/metadata/1024":
                return open(FAKE_MOVIE_ONE_XML)
            if url.path == "/library/metadata/1135":
                return open(FAKE_MOVIE_TWO_XML)
            if url.path == "/library/metadata/425/children":
                return open(FAKE_TV_SEASONS_XML)
            if url.path == "/library/metadata/426/children":
                return open(FAKE_TV_EPISODES_XML)
            if url.path == "/library/metadata/433/children":
                return open(FAKE_TV_EPISODE_XML)
            if url.path == "/library/metadata/2251":
                return open(FAKE_TV_EPISODE_METADATA_XML)
            if url.path == "/library/metadata/2448":
                return open(FAKE_TV_EPISODE_2448_XML)
            if url.path == "/library/metadata/2254":
                return open(FAKE_TV_EPISODE_2254_XML)
            if url.path == "/library/metadata/2257":
                return open(FAKE_TV_EPISODE_2257_XML)
            if url.path == "/library/metadata/433":
                return open(FAKE_TV_EPISODE_433_XML)
            if url.path == "/library/metadata/2":
                return open(FAKE_SECTION_2_XML)
            raise ValueError("Unknown request: %s" % url.path)

        def fake_open_config_file(self):
            return StringIO.StringIO(FAKE_CONFIG_FILE)

        self.useFixture(fixtures.NestedTempfile())
        self.stdout = self.useFixture(fixtures.StringStream('stdout')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.stdout))
        stderr = self.useFixture(fixtures.StringStream('stderr')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
        self.logger = self.useFixture(fixtures.FakeLogger(name="plexpiry"))
        self.useFixture(fixtures.MonkeyPatch('urllib2.urlopen', fake_urlopen))
        self.useFixture(fixtures.MonkeyPatch('plexpiry.plexpiry.Plexpiry.open_\
                                              config_file',
                                             fake_open_config_file))
        self.addCleanup(self.cleanUp)

        self.options = FakeOptions()
        self.plexpiry = plexpiry.Plexpiry(self.options)
        self.plexpiry.find_sections()

    def cleanUp(self):
        self.options = FakeOptions()

    def test_urlbase(self):
        self.assertEqual("http://fakeserver:fakeport", self.plexpiry.urlbase)

    def test_dbg_silence(self):
        self.plexpiry.dbg("test_dbg_silence")
        self.stdout.seek(0)
        self.assertEqual('', self.stdout.read().strip())

    def test_dbg_noise(self):
        self.options.debug = True
        self.plexpiry.dbg("test_dbg_noise")
        self.stdout.seek(0)
        self.assertEqual("DEBUG: test_dbg_noise", self.stdout.read().strip())

    def test_err(self):
        self.plexpiry.err("test_err")
        self.stdout.seek(0)
        self.assertEqual("ERROR: test_err", self.stdout.read().strip())

    def test_info(self):
        self.plexpiry.info("test_info")
        self.stdout.seek(0)
        self.assertEqual("INFO: test_info", self.stdout.read().strip())

    def test_trim_dict(self):
        expected_dict = \
            {
                'a': 1,
                'd': 4,
            }
        new_dict = self.plexpiry.trim_dict(FAKE_DICT, ['a', 'd'])
        self.assertEqual(expected_dict, new_dict)

    def test_parse_time_bare(self):
        self.assertEqual(1, self.plexpiry.parse_time('1'))

    def test_parse_time_days(self):
        self.assertEqual(86400, self.plexpiry.parse_time('1d'))

    def test_parse_time_weeks(self):
        self.assertEqual(86400 * 7, self.plexpiry.parse_time('1w'))

    def test_parse_time_years(self):
        self.assertEqual(86400 * 365, self.plexpiry.parse_time('1y'))

    def test_parse_time_bogus(self):
        self.assertRaises(ValueError, self.plexpiry.parse_time, 'bogus')

    def test_parse_time_negative(self):
        self.assertRaises(ValueError, self.plexpiry.parse_time, '-1')

    def test_find_sections(self):
        self.assertEqual(FAKE_SECTIONS, self.plexpiry.sections)

    def test_find_tv_shows(self):
        shows = self.plexpiry.find_tv_shows()
        self.assertEqual(FAKE_TV_SHOWS, shows)

    def test_find_tv_seasons(self):
        seasons = self.plexpiry.find_tv_seasons(TEST_TV_SHOW)
        self.assertEqual(FAKE_TV_SEASONS, seasons)

    def test_find_tv_episodes(self):
        episodes = self.plexpiry.find_tv_episodes(TEST_TV_SHOW, TEST_TV_SEASON)
        self.assertEqual(FAKE_TV_EPISODES, episodes)

    def test_get_tv_episode(self):
        episode = self.plexpiry.get_tv_episode(TEST_TV_EPISODE)
        self.assertEqual(FAKE_TV_EPISODE, episode)

    def test_get_movies(self):
        movies = self.plexpiry.get_movie_tree()
        self.assertEqual(FAKE_MOVIES, movies)

    def test_get_movie(self):
        movie = self.plexpiry.get_movie(TEST_MOVIE)
        self.assertEqual(FAKE_MOVIE_ONE, movie)
