import ConfigParser
import fixtures
import os
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
FAKE_TV_TREE = {'425':
                {'seasons':
                 {'426':
                  {'episodes':
                   {'433':
                    {'addedAt': '1401322741',
                     'lastViewedAt': '1401322997',
                     'originallyAvailableAt': '2007-05-21',
                     'ratingKey': '433',
                     'title': 'Episode 7',
                     'viewCount': '1'}},
                   'title': 'Season 1'},
                     '434':
                     {'episodes':
                      {'433':
                       {'addedAt': '1401322741',
                        'lastViewedAt': '1401322997',
                        'originallyAvailableAt': '2007-05-21',
                        'ratingKey': '433',
                        'title': 'Episode 7',
                        'viewCount': '1'}},
                      'title': 'Season 2'}},
                 'title': 'Spaced'}}
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
FAKE_TV_TREE_XML = os.path.join(FAKE_PATH, "fake_tv_tree.xml")
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

GOOD_CONFIG_FILE = os.path.join(FAKE_PATH, "good_config_file.conf")
BAD_CONFIG_FILE = os.path.join(FAKE_PATH, "bad_config_file.conf")
BAD_CONFIG_FILE2 = os.path.join(FAKE_PATH, "bad_config_file2.conf")
EMPTY_CONFIG_FILE = os.path.join(FAKE_PATH, "empty_file")
NON_EXPIRING_CONFIG_FILE = os.path.join(FAKE_PATH,
                                        "non_expiring_config_file.conf")
IGNORE_CONFIG_FILE = os.path.join(FAKE_PATH, "ignore.conf")
NEVER_EXPIRE_CONFIG_FILE = os.path.join(FAKE_PATH, "never_expire.conf")

FAKE_EMPTY = os.path.join(FAKE_PATH, "empty_file")

TEST_TV_SHOW = 425
TEST_TV_SEASON = 426
TEST_TV_EPISODE = 433
TEST_MOVIE = 1024

FAKE_OPTIONS = ["-s", "fakeserver", "-p", "1234", "-c", GOOD_CONFIG_FILE]
FAKE_BADCONFIGFILE_OPTIONS = ["-s", "fakeserver", "-p", "1234",
                              "-c", BAD_CONFIG_FILE]


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
            if url.path == "/library/sections/1/refresh":
                return open(FAKE_EMPTY)
            if url.path == "/library/sections/2/refresh":
                return open(FAKE_EMPTY)
            if url.path == "/library/metadata/434/children":
                return open(FAKE_TV_TREE_XML)
            raise ValueError("Unknown request: %s" % url.path)

        self.useFixture(fixtures.NestedTempfile())
        self.stdout = self.useFixture(fixtures.StringStream('stdout')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.stdout))
        stderr = self.useFixture(fixtures.StringStream('stderr')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
        self.logger = self.useFixture(fixtures.FakeLogger(name="plexpiry"))
        self.useFixture(fixtures.MonkeyPatch('urllib2.urlopen', fake_urlopen))
        self.addCleanup(self.cleanUp)

        self.options = plexpiry.parse_options(FAKE_OPTIONS)
        self.plexpiry = plexpiry.Plexpiry(self.options)
        self.plexpiry.find_sections()

    def cleanUp(self):
        self.options = plexpiry.parse_options(FAKE_OPTIONS)

    def test_urlbase(self):
        self.assertEqual("http://fakeserver:1234", self.plexpiry.urlbase)

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

    def test_open_config_file(self):
        data = self.plexpiry.open_config_file().read()
        self.assertEqual(open(GOOD_CONFIG_FILE).read(), data)

    def test_good_config_file(self):
        self.plexpiry = plexpiry.Plexpiry(self.options)
        self.plexpiry.load_config()

    def test_bad_config_file(self):
        self.plexpiry = plexpiry.Plexpiry(self.options)
        self.options.config_file = BAD_CONFIG_FILE
        self.assertRaises(ConfigParser.ParsingError, self.plexpiry.load_config)

        self.options.config_file = BAD_CONFIG_FILE2
        self.assertRaises(ConfigParser.MissingSectionHeaderError,
                          self.plexpiry.load_config)

        self.assertRaises(ConfigParser.ParsingError,
                          plexpiry.Plexpiry,
                          plexpiry.parse_options(FAKE_BADCONFIGFILE_OPTIONS))

    def test_empty_config_file(self):
        self.plexpiry = plexpiry.Plexpiry(self.options)
        self.options.config_file = EMPTY_CONFIG_FILE
        self.plexpiry.load_config()

    def test_get_config_sections(self):
        self.assertEqual(['global', 'movies', 'tv'],
                         self.plexpiry.get_config_sections())

    def test_get_config_section(self):
        self.assertEqual({'watched': '30d',
                          'unwatched': '90d'},
                         self.plexpiry.get_config_section("global"))

    def test_get_config_no_section(self):
        self.assertEqual(None, self.plexpiry.get_config_section("bogus"))

    def test_collapse_config(self):
        self.assertEqual({'__name': 'Spaced',
                          'unwatched': '90d',
                          'watched': '30d',
                          'aired': '365d'},
                         self.plexpiry.collapse_config("Spaced", "tv"))

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

    def test_get_tv_tree(self):
        self.assertEquals(FAKE_TV_TREE, self.plexpiry.get_tv_tree())

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

    def test_is_watched(self):
        movie = self.plexpiry.get_movie(TEST_MOVIE)
        self.assertEqual(True, self.plexpiry.is_watched(movie))

    def test_refresh_plex(self):
        self.plexpiry.refresh_plex()
        self.options.dryrun = True
        self.plexpiry.refresh_plex()

    def test_should_expire_media_watched(self):
        movie = self.plexpiry.get_movie(TEST_MOVIE)

        config = self.plexpiry.collapse_config(movie["title"], "movies")
        self.assertEqual(['watched'],
                         self.plexpiry.should_expire_media(movie, config))

    def test_should_expire_media_watched_aired(self):
        show = self.plexpiry.get_tv_episode(TEST_TV_EPISODE)
        self.options.config_file = GOOD_CONFIG_FILE
        self.plexpiry.load_config()
        config = self.plexpiry.collapse_config("Spaced", "tv")
        self.assertEqual(['watched', 'aired'],
                         self.plexpiry.should_expire_media(show,
                                                           config))

    def test_should_expire_media_noconfig(self):
        show = self.plexpiry.get_tv_episode(TEST_TV_EPISODE)
        self.options.config_file = EMPTY_CONFIG_FILE
        self.plexpiry.load_config()
        config = self.plexpiry.collapse_config("Spaced", "tv")
        self.assertEqual(False, self.plexpiry.should_expire_media(show,
                                                                  config))

    def test_should_expire_media_notexpired(self):
        show = self.plexpiry.get_tv_episode(TEST_TV_EPISODE)
        self.options.config_file = NEVER_EXPIRE_CONFIG_FILE
        self.plexpiry.load_config()
        config = self.plexpiry.collapse_config("Spaced", "tv")
        self.assertEqual(False, self.plexpiry.should_expire_media(show,
                                                                  config))

    def test_should_expire_media_notwatched_aired(self):
        show = self.plexpiry.get_tv_episode(TEST_TV_EPISODE)
        del(show["lastViewedAt"])
        self.options.config_file = NON_EXPIRING_CONFIG_FILE
        self.plexpiry.load_config()
        config = self.plexpiry.collapse_config("Spaced", "tv")
        self.assertEqual(['unwatched'],
                         self.plexpiry.should_expire_media(show, config))

    def test_should_expire_media_ignored(self):
        show = self.plexpiry.get_tv_episode(TEST_TV_EPISODE)
        self.options.config_file = IGNORE_CONFIG_FILE
        self.plexpiry.load_config()
        config = self.plexpiry.collapse_config("Spaced", "tv")
        self.assertEqual(False, self.plexpiry.should_expire_media(show,
                                                                  config))

    def test_delete(self):
        show = self.plexpiry.get_tv_episode(TEST_TV_EPISODE)
        self.options.dryrun = True
        self.options.debug = True
        self.plexpiry.delete(show["ratingKey"])
        self.stdout.seek(0)
        data = self.stdout.read().strip()
        self.assertIn("DELETE http://fakeserver:1234/library/metadata/433",
                      data)

    def test_parse_options(self):
        args = ['-d', '-n', '-s', 'foo', '-p', '123', '-c', 'bar']
        options = {"debug": True,
                   "dryrun": True,
                   "server": "foo",
                   "port": 123,
                   "config_file": "bar"}

        self.assertEqual(options, vars(plexpiry.parse_options(args)))

    def test_parse_options_partial(self):
        args = ['-s', 'foo']
        options = {"debug": False,
                   "dryrun": False,
                   "server": "foo",
                   "port": 32400,
                   "config_file": "~/.config/plexpiry.conf"}
        self.assertEqual(options, vars(plexpiry.parse_options(args)))

    def test_expire(self):
        self.options.dryrun = True
        self.plexpiry.expire()

    def test_expire_ignore_all(self):
        self.options.dryrun = True
        self.options.config_file = IGNORE_CONFIG_FILE
        self.plexpiry.load_config()
        self.plexpiry.expire()
