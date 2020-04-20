import json
import logging
import sys

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LicenseType
from galaxy.api.types import NextStep, Authentication, Game, LicenseInfo
from galaxy.api.errors import AuthenticationRequired
from galaxy.http import HttpClient


AUTH_PARAMS = {
    "window_title": "Login to Indie Gala",
    "window_width": 400,
    "window_height": 680,
    "start_uri": f"https://www.indiegala.com/login",
    "end_uri_regex": r"https://www\.indiegala\.com"
}

VERSION = "0.1"

SHOWCASE_URL = 'https://www.indiegala.com/showcase_collection'
USER_INFO_URL = 'https://www.indiegala.com/get_user_info'


class IndieGalaPlugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(
            Platform.IndieGala,
            VERSION,
            reader,
            writer,
            token
        )
        self.http_client = HttpClient()
        self.session_cookie = None

    # implement methods
    async def authenticate(self, stored_credentials=None):
        logging.debug("Calling authenticate")
        if not stored_credentials:
            return NextStep("web_session", AUTH_PARAMS)
        self.session_cookie = stored_credentials
        return self.get_user_info()

    async def pass_login_credentials(self, step, credentials, cookies):
        """Called just after CEF authentication (called as NextStep by authenticate)"""
        session_cookie = None
        for cookie in cookies:
            if cookie['name'] == 'auth':
                value = cookie['value']
                session_cookie = {'auth': value}
                break
        self.store_credentials(session_cookie)
        self.session_cookie = session_cookie
        return self.get_user_info()

    async def get_owned_games(self):
        html = await self.retrieve_showcase_html()
        games = [game for game in self.parse_html_into_games(html)]
        return games

    async def get_user_info(self):
        if not self.session_cookie:
            raise AuthenticationRequired()
        response = await self.http_client.request('get', USER_INFO_URL, cookies=self.session_cookie, allow_redirects=False)
        text = await response.text()
        data = json.loads(text)
        return Authentication(data['profile'], data['email'])

    async def retrieve_showcase_html(self):
        if not self.session_cookie:
            raise AuthenticationRequired()

        response = await self.http_client.request('get', SHOWCASE_URL, cookies=self.session_cookie, allow_redirects=False)
        text = await response.text()
        data = json.loads(text)
        return data['html']

    def parse_html_into_games(self, html):
        lines = html.split('<div class=\"col-xs-4\">\r\n\t\t\t\t\t')
        for line in lines:
            if not line.startswith('<a'):
                continue
            game_line = line.split('</a>')[0]
            game_name = game_line.split('>')[1]
            logging.debug(game_name)
            yield Game(
                game_id=game_name,
                game_title=game_name,
                license_info=LicenseInfo(LicenseType.SinglePurchase),
                dlcs=[]
            )


def main():
    create_and_run_plugin(IndieGalaPlugin, sys.argv)


# run plugin event loop
if __name__ == "__main__":
    main()
