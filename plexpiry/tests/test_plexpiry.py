import fixtures
import testtools

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


class FakeOptions():
    debug = False
    server = "fakeserver"
    port = "fakeport"


class TestPlexpiry(testtools.TestCase):

    def setUp(self):
        super(TestPlexpiry, self).setUp()
        self.useFixture(fixtures.NestedTempfile())
        self.stdout = self.useFixture(fixtures.StringStream('stdout')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.stdout))
        stderr = self.useFixture(fixtures.StringStream('stderr')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
        self.logger = self.useFixture(fixtures.FakeLogger(name="plexpiry"))
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
