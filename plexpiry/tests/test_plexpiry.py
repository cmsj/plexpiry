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
FAKE_SECTIONS = {'show': 3,
                 'movies': 5,
                 }

FAKE_PATH = os.path.dirname(__file__)
FAKE_SECTIONS_XML = os.path.join(FAKE_PATH, "fake_sections.xml")
FAKE_TV_SHOWS = os.path.join(FAKE_PATH, "fake_tv_shows.xml")
FAKE_TV_SEASONS = os.path.join(FAKE_PATH, "fake_tv_seasons.xml")
FAKE_TV_EPISODES = os.path.join(FAKE_PATH, "fake_tv_episodes.xml")
FAKE_TV_EPISODE = os.path.join(FAKE_PATH, "fake_tv_episode.xml")
FAKE_MOVIES = os.path.join(FAKE_PATH, "fake_movies.xml")
FAKE_MOVIE = os.path.join(FAKE_PATH, "fake_movie.xml")


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
            raise ValueError("Unknown request: %s" % url.path)

        self.useFixture(fixtures.NestedTempfile())
        self.stdout = self.useFixture(fixtures.StringStream('stdout')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.stdout))
        stderr = self.useFixture(fixtures.StringStream('stderr')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
        self.logger = self.useFixture(fixtures.FakeLogger(name="plexpiry"))
        self.useFixture(fixtures.MonkeyPatch('urllib2.urlopen', fake_urlopen))
        self.addCleanup(self.cleanUp)

        self.options = FakeOptions()
        self.plexpiry = plexpiry.Plexpiry(self.options)

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
        self.plexpiry.find_sections()
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
        self.assertEqual(FAKE_MOVIE, movie)
