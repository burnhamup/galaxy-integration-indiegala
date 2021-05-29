import json
from pathlib import Path
import sys

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LicenseType
from galaxy.api.types import NextStep, Authentication, Game, LicenseInfo
from galaxy.api.errors import AuthenticationRequired

from http_client import HTTPClient

with open(Path(__file__).parent / 'manifest.json', 'r') as f:
    __version__ = json.load(f)['version']

END_URI_REGEX = r"^https://www\.indiegala\.com/?(#.*)?$"

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

SECURITY_JS = {r"^https://www\.indiegala\.com/.*": [
    r'''
        if (document.getElementsByTagName('title')[0].text.includes("Library | Indiegala")) {
            window.location.href = "/";
        }
    '''
]}  # Redirects to the homepage if the library loads normally

HOMEPAGE = 'https://www.indiegala.com'

SHOWCASE_API = 'https://www.indiegala.com/login_new/user_info'


class IndieGalaPlugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(
            Platform.IndieGala,
            __version__,
            reader,
            writer,
            token
        )
        self.http_client = HTTPClient(self.store_credentials)
        self.session_cookie = None

    async def shutdown(self):
        await self.http_client.close()

    # implement methods
    async def authenticate(self, stored_credentials=None):
        if not stored_credentials:
            return NextStep("web_session", AUTH_PARAMS)
        self.http_client.update_cookies(stored_credentials)
        try:
            return await self.get_user_info()
        except AuthenticationRequired:
            return NextStep("web_session", SECURITY_AUTH_PARAMS, cookies=self.http_client.get_next_step_cookies(), js=SECURITY_JS)

    async def pass_login_credentials(self, step, credentials, cookies):
        """Called just after CEF authentication (called as NextStep by authenticate)"""
        session_cookies = {cookie['name']: cookie['value'] for cookie in cookies if cookie['name']}
        self.http_client.update_cookies(session_cookies)
        try:
            return await self.get_user_info()
        except AuthenticationRequired:
            return NextStep("web_session", SECURITY_AUTH_PARAMS, cookies=self.http_client.get_next_step_cookies(), js=SECURITY_JS)

    async def get_owned_games(self):
        text = await self.http_client.get(SHOWCASE_API)
        data = json.loads(text)
        games_json = data['showcase_content']['content']['user_collection']
        result = []
        for game_json in games_json:
            game = Game(
                game_id=game_json['prod_slugged_name'],
                game_title=game_json['prod_name'],
                license_info=LicenseInfo(LicenseType.SinglePurchase),
                dlcs=[]
            )
            result.append(game)
        return result

    async def get_user_info(self):
        text = await self.http_client.get(SHOWCASE_API)
        data = json.loads(text)

        return Authentication(data['_indiegala_user_id'], data['_indiegala_username'])


def main():
    create_and_run_plugin(IndieGalaPlugin, sys.argv)


# run plugin event loop
if __name__ == "__main__":
    main()
