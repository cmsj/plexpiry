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
FAKE_SECTIONS = {'show': {'key': '5', 'title': 'TV Shows'},
                 'movie': {'key': '3', 'title': 'Movies'},
                 }
FAKE_TV_SHOWS = {'1032': {'title': 'TV Show One'},
                 '813': {'title': 'TV Show Two'},
                 }
FAKE_TV_SEASONS = {'2250': {'title': 'Season 1'}}
FAKE_TV_EPISODES = {'2251': {'addedAt': '1381952103',
                             'ratingKey': '2251',
                             'title': 'Episode 1'},
                    '2254': {'addedAt': '1381952561',
                             'ratingKey': '2254',
                             'title': 'Episode 2'},
                    '2257': {'addedAt': '1381952990',
                             'ratingKey': '2257',
                             'title': 'Episode 3'},
                    '2260': {'addedAt': '1381953455',
                             'ratingKey': '2260',
                             'title': 'Episode 4'}
                    }
FAKE_TV_EPISODE = {'addedAt': '1381953455',
                   'art': '/library/metadata/2249/art/1381952116',
                   'contentRating': 'TV-PG',
                   'duration': '2570938',
                   'grandparentKey': '/library/metadata/2249',
                   'grandparentRatingKey': '2249',
                   'grandparentThumb': '/library/metadata/2249/thumb/'
                                       '1381952116',
                   'grandparentTitle': 'State of Play',
                   'guid': 'com.plexapp.agents.thetvdb://80383/1/4?lang=en',
                   'index': '4',
                   'key': '/library/metadata/2260',
                   'originallyAvailableAt': '2003-06-08',
                   'parentIndex': '1',
                   'parentKey': '/library/metadata/2250',
                   'parentRatingKey': '2250',
                   'parentThumb': '/library/metadata/2250/thumb/1381952116',
                   'rating': '7',
                   'ratingKey': '2260',
                   'summary': "Foy is questioned by the news team at a hotel "
                              "and his interview is recorded by Syd in the "
                              "next room, who later discovers personally that "
                              "Foy is gay. Cal declares his love for Anne. "
                              "Cameron Foster persuades Stephen Collins not to"
                              " tell the tabloid press about Anne and Cal's "
                              "affair. Foy has been paid by Warner Schloss who"
                              " are lobbyists for U-EX Oil. Was Sonia a spy "
                              "for the company? Meanwhile Stephen discovers he"
                              " has had a weekend away with Sonia for which "
                              "their expenses were also paid by Warner- "
                              "Schloss.",
                   'thumb': '/library/metadata/2260/thumb/1381953455',
                   'title': 'Episode 4',
                   'type': 'episode',
                   'year': '2003'
                   }
FAKE_MOVIES = {'1953': {'addedAt': '1372976363',
                        'lastViewedAt': '1379106772',
                        'ratingKey': '1953',
                        'title': 'Movie Two',
                        'viewCount': '1'},
               '802': {'addedAt': '1365089389',
                       'ratingKey': '802',
                       'title': 'Movie One'}}
FAKE_MOVIE_ONE = {'addedAt': '1365089389',
                  'art': '/library/metadata/802/art/1365091926',
                  'duration': '5415577',
                  'guid': 'com.plexapp.agents.imdb://tt123456?lang=en',
                  'key': '/library/metadata/802',
                  'originallyAvailableAt': '2013-11-17',
                  'ratingKey': '802',
                  'studio': 'Movie Films',
                  'summary': "Movie One is the first movie",
                  'tagline': 'A movie',
                  'thumb': '/library/metadata/802/thumb/1365091926',
                  'title': "Movie One",
                  'type': 'movie',
                  'updatedAt': '1365091926',
                  'year': '2013'
                  }
FAKE_PATH = os.path.dirname(__file__)
FAKE_SECTIONS_XML = os.path.join(FAKE_PATH, "fake_sections.xml")
FAKE_TV_SHOWS_XML = os.path.join(FAKE_PATH, "fake_tv_shows.xml")
FAKE_TV_SEASONS_XML = os.path.join(FAKE_PATH, "fake_tv_seasons.xml")
FAKE_TV_EPISODES_XML = os.path.join(FAKE_PATH, "fake_tv_episodes.xml")
FAKE_TV_EPISODE_XML = os.path.join(FAKE_PATH, "fake_tv_episode.xml")
FAKE_TV_EPISODE_METADATA_XML = os.path.join(FAKE_PATH,
                                            "fake_tv_episode_metadata.xml")
FAKE_TV_EPISODE_2448_XML = os.path.join(FAKE_PATH, "2448.xml")
FAKE_TV_EPISODE_2254_XML = os.path.join(FAKE_PATH, "2254.xml")
FAKE_TV_EPISODE_2257_XML = os.path.join(FAKE_PATH, "2257.xml")
FAKE_TV_EPISODE_2260_XML = os.path.join(FAKE_PATH, "2260.xml")
FAKE_MOVIES_XML = os.path.join(FAKE_PATH, "fake_movies.xml")
FAKE_MOVIE_ONE_XML = os.path.join(FAKE_PATH, "fake_movie_one.xml")
FAKE_MOVIE_TWO_XML = os.path.join(FAKE_PATH, "fake_movie_two.xml")

TEST_TV_SHOW = 2249
TEST_TV_SEASON = 2250
TEST_TV_EPISODE = 2260
TEST_MOVIE = 802


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
            if url.path == "/library/sections/3/all":
                return open(FAKE_MOVIES_XML)
            if url.path == "/library/sections/5/all":
                return open(FAKE_TV_SHOWS_XML)
            if url.path == "/library/metadata/802":
                return open(FAKE_MOVIE_ONE_XML)
            if url.path == "/library/metadata/1953":
                return open(FAKE_MOVIE_TWO_XML)
            if url.path == "/library/metadata/2249/children":
                return open(FAKE_TV_SEASONS_XML)
            if url.path == "/library/metadata/2250/children":
                return open(FAKE_TV_EPISODES_XML)
            if url.path == "/library/metadata/2260/children":
                return open(FAKE_TV_EPISODE_XML)
            if url.path == "/library/metadata/2251":
                return open(FAKE_TV_EPISODE_METADATA_XML)
            if url.path == "/library/metadata/2448":
                return open(FAKE_TV_EPISODE_2448_XML)
            if url.path == "/library/metadata/2254":
                return open(FAKE_TV_EPISODE_2254_XML)
            if url.path == "/library/metadata/2257":
                return open(FAKE_TV_EPISODE_2257_XML)
            if url.path == "/library/metadata/2260":
                return open(FAKE_TV_EPISODE_2260_XML)
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
