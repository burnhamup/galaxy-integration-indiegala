
from unittest import TestCase

from src.plugin import END_URI_REGEX


class TestIndieGalaPlugin(TestCase):
    def test_end_uri_regex(self):
        self.assertRegex('https://www.indiegala.com/', END_URI_REGEX)
        self.assertRegex('https://www.indiegala.com', END_URI_REGEX)
        self.assertRegex('https://www.indiegala.com#', END_URI_REGEX)
        self.assertRegex('https://www.indiegala.com/#_=_', END_URI_REGEX)
        self.assertNotRegex('https://www.indiegala.com/login', END_URI_REGEX)


