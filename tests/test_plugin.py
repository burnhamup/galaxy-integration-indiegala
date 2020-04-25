import json
from unittest import TestCase

from galaxy.api.consts import LicenseType
from galaxy.api.types import Game, LicenseInfo

from src.plugin import IndieGalaPlugin


class TestIndieGalaPlugin(TestCase):
    def test_parse_html_into_games(self):
        with open('fixtures/showcase.json', 'r') as fixture:
            raw_response = fixture.read()
        data = json.loads(raw_response)

        actual_games = [game for game in IndieGalaPlugin.parse_html_into_games(data['html'])]
        expected_games = [
            Game('Survivalist', 'Survivalist', [], LicenseInfo(LicenseType.SinglePurchase)),
            Game('Galactic Missile Defense', 'Galactic Missile Defense', [], LicenseInfo(LicenseType.SinglePurchase)),
            Game('Super Destronaut', 'Super Destronaut', [], LicenseInfo(LicenseType.SinglePurchase)),
            Game('TheFan', 'TheFan', [], LicenseInfo(LicenseType.SinglePurchase)),
        ]
        # Actually asserts that the lists have the same items, but they don't have to be in the same order
        self.assertCountEqual(expected_games, actual_games)
