import requests


class XfinityControlException(Exception):
    pass


class XfinityLoginException(XfinityControlException):
    pass


class XfinityApiException(XfinityControlException):
    pass


class XfinityControl(object):
    LOGIN_URL = "https://login.comcast.net/login"
    API_PREFIX = "http://xfinitytv.comcast.net"
    PROFILE_API = API_PREFIX + "/xtv/authkey/user"
    TOKEN_API = API_PREFIX + "/xip/fc-rproxy/rtune/authtoken"
    CHANNEL_API = API_PREFIX + "/xip/fc-rproxy/rtune/device/%s/tune/tv/vcn/%s"
    LISTING_API = API_PREFIX + "/xfinityapi/channel/lineup/headend/%s/"

    PROFILE_TOKEN_LENGTH = 32

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._auth_cookies = self._login()
        self._profile = self._get_profile()
        self._token = self._get_token()
        self._default_device_key = self._profile['UnifiedVal']['udf']['devices'][0]['rtune']['deviceKey']
        try:
            self._headend = self._profile["UnifiedVal"]["uisTvPrefs"]["rovi"]["headend"]
            self._default_lineup = self._get_lineup()
            self.channel_map = {
                x["_embedded"]["station"]["shortName"]: x["number"]
                for x in self._default_lineup["_embedded"]["channels"]
            }
        except KeyError:
            self._headend = None
            self._default_lineup = None
            self.channel_map = {}
        super(XfinityControl, self).__init__()

    def _login(self):
        cookie_request = requests.get(
            XfinityControl.LOGIN_URL,
            allow_redirects=False,
        )
        login_request = requests.post(
            XfinityControl.LOGIN_URL,
            data={
                "user": self._username,
                "passwd": self._password
            },
            cookies=cookie_request.cookies,
            allow_redirects=False,
        )
        if login_request.cookies.get("s_ticket") is None:
            raise XfinityLoginException("Authentication Failure.")
        return login_request.cookies

    def _get_profile(self):
        profile_request = requests.get(
            XfinityControl.PROFILE_API,
            params={
                "p": self._auth_cookies["s_ticket"][:XfinityControl.PROFILE_TOKEN_LENGTH]
            },
            cookies=self._auth_cookies,
        )
        if profile_request.status_code != 200:
            raise XfinityApiException("Unexpected profile API response.")
        return profile_request.json()

    def _get_token(self):
        token_request = requests.get(
            XfinityControl.TOKEN_API,
            cookies=self._auth_cookies,
        )
        if token_request.status_code != 200:
            raise XfinityApiException("Unexpected token API response.")
        return token_request.text

    def _get_lineup(self):
        if self._headend is None:
            return None
        lineup_request = requests.get(
            XfinityControl.LISTING_API % self._headend,
            cookies=self._auth_cookies,
        )
        if lineup_request.status_code != 200:
            raise XfinityApiException("Unexpected profile API response.")
        return lineup_request.json()

    def _refresh_token(self):
        self._auth_cookies = self._login()
        self._token = self._get_token()

    def change_channel(self, channel, retries_remaining=1):
        change_channel_request = requests.post(
            XfinityControl.CHANNEL_API % (self._default_device_key, channel),
            headers={
                "X-CIM-RT-Authorization": self._token
            },
            cookies=self._auth_cookies,
        )
        if change_channel_request.status_code == 401 and retries_remaining > 0:
            self._refresh_token()
            self.change_channel(channel, retries_remaining - 1)
        elif change_channel_request.status_code != 200:
            raise XfinityApiException("Unexpected channel API response.")
