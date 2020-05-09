import json
import logging
from pathlib import Path
import sys

from bs4 import BeautifulSoup
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LicenseType
from galaxy.api.types import NextStep, Authentication, Game, LicenseInfo
from galaxy.api.errors import AuthenticationRequired
from galaxy.http import HttpClient

with open(Path(__file__).parent / 'manifest.json', 'r') as f:
    __version__ = json.load(f)['version']

END_URI_REGEX = r"^https://www\.indiegala\.com/?(library)?(#.*)?$"

AUTH_PARAMS = {
    "window_title": "Login to Indiegala",
    "window_width": 1000,
    "window_height": 800,
    "start_uri": f"https://www.indiegala.com/login",
    "end_uri_regex": END_URI_REGEX,
}

# To hopefully be shown when either the IP check or the Captcha appears
SECURITY_AUTH_PARAMS = {
    "window_title": "Indiegala Security Check",
    "window_width": 1000,
    "window_height": 800,
    "start_uri": f"https://www.indiegala.com/library",
    "end_uri_regex": END_URI_REGEX,
}

SHOWCASE_URL = 'https://www.indiegala.com/library/showcase/%s'

HOMEPAGE = 'https://www.indiegala.com'


class IndieGalaPlugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(
            Platform.IndieGala,
            __version__,
            reader,
            writer,
            token
        )
        self.http_client = HttpClient()
        self.session_cookie = None

    # implement methods
    async def authenticate(self, stored_credentials=None):
        if not stored_credentials:
            return NextStep("web_session", AUTH_PARAMS)
        self.session_cookies = stored_credentials
        try:
            return await self.get_user_info()
        except AuthenticationRequired:
            return NextStep("web_session", AUTH_PARAMS)

    async def pass_login_credentials(self, step, credentials, cookies):
        """Called just after CEF authentication (called as NextStep by authenticate)"""
        session_cookies = {cookie['name']: cookie['value'] for cookie in cookies if cookie['name']}
        self.store_credentials(session_cookies)
        self.session_cookies = session_cookies
        return await self.get_user_info()

    async def get_owned_games(self):
        page = 1
        games = []
        while True:
            raw_html = await self.retrieve_showcase_html(page)
            if 'Your showcase list is actually empty.' in raw_html:
                return games
            if 'Profile locked' in raw_html:
                logging.debug('IP check required')
                self.lost_authentication()
                raise AuthenticationRequired()
            if '_Incapsula_Resource' in raw_html:
                logging.debug('Incapsula challenge on showcase page %s', page)
                self.lost_authentication()
                raise AuthenticationRequired()
            soup = BeautifulSoup(raw_html)
            games.extend(self.parse_html_into_games(soup))
            page += 1

    async def get_user_info(self):
        if not self.session_cookies:
            raise AuthenticationRequired()
        response = await self.http_client.request('get', HOMEPAGE, cookies=self.session_cookies, allow_redirects=False)
        text = await response.text()
        if '_Incapsula_Resource' in text:
            logging.debug('Incapsula challenge on get_user_info')
            # TODO try returning a NextStep() to open a browser. Can I open a next step to /library?
            raise AuthenticationRequired()
        if 'Profile locked' in text:
            logging.debug('IP check required')
            raise AuthenticationRequired()
        soup = BeautifulSoup(text)
        username_div = soup.select('div.username-text')[0]
        username = str(username_div.string)
        return Authentication(username, username)

    async def retrieve_showcase_html(self, n=1):
        if not self.session_cookies:
            raise AuthenticationRequired()
        response = await self.http_client.request('get', SHOWCASE_URL % n, cookies=self.session_cookies, allow_redirects=False)
        text = await response.text()
        return text

    @staticmethod
    def parse_html_into_games(soup):
        games = soup.select('a.library-showcase-title')
        for game in games:
            game_name = str(game.string)
            game_href = game['href']
            url_slug = str(game_href.split('indiegala.com/')[1])
            logging.debug('Parsed %s, %s', game_name, url_slug)
            yield Game(
                game_id=url_slug,
                game_title=game_name,
                license_info=LicenseInfo(LicenseType.SinglePurchase),
                dlcs=[]
            )


def main():
    create_and_run_plugin(IndieGalaPlugin, sys.argv)


# run plugin event loop
if __name__ == "__main__":
    main()
