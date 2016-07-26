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

    PROFILE_TOKEN_LENGTH = 32

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth_cookies = self._login()
        self.profile = self._get_profile()
        self.default_device_key = self.profile['UnifiedVal']['udf']['devices'][0]['rtune']['deviceKey']
        self.token = self._get_token()
        super(XfinityControl, self).__init__()

    def _login(self):
        cookie_request = requests.get(
            XfinityControl.LOGIN_URL,
            allow_redirects=False,
        )
        login_request = requests.post(
            XfinityControl.LOGIN_URL,
            data={
                "user": self.username,
                "passwd": self.password
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
                "p": self.auth_cookies["s_ticket"][:XfinityControl.PROFILE_TOKEN_LENGTH]
            },
            cookies=self.auth_cookies,
        )
        if profile_request.status_code != 200:
            raise XfinityApiException("Unexpected profile API response.")
        return profile_request.json()

    def _get_token(self):
        token_request = requests.get(
            XfinityControl.TOKEN_API,
            cookies=self.auth_cookies,
        )
        if token_request.status_code != 200:
            raise XfinityApiException("Unexpected token API response.")
        return token_request.text

    def change_channel(self, param):
        change_channel_request = requests.post(
            XfinityControl.CHANNEL_API % (self.default_device_key, param),
            headers={
                "X-CIM-RT-Authorization": self.token
            },
            cookies=self.auth_cookies,
        )
        if change_channel_request.status_code != 200:
            raise XfinityApiException("Unexpected channel API response.")
