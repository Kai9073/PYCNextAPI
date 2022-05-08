import requests
from pycnetTypes import baseUrl


class CredentialsError(Exception):
    pass


class Pypyc():
    def __init__(self):
        self.baseUrl = baseUrl
        self.headers = {
            "credentials": "include",
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0)" +
            "Gecko/20100101 Firefox/100.0",
            "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9," +
            "image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "mode": "cors"
        }
        self.session = requests.Session()

    def get(self, url: str, _headers: dict = {}) -> requests.Response:
        headers = self.headers
        headers["method"] = "GET"
        for header in _headers:
            headers[header] = _headers[header]
        response = self.session.get(url, headers=headers)
        return response

    def post(self,
             url: str,
             _headers: dict = {},
             body: dict = {}) -> requests.Response:
        headers = self.headers
        headers["method"] = "POST"
        for header in _headers:
            headers[header] = _headers[header]

        response = self.session.post(url, headers=_headers, data=body)
        return response

    def getCreds(self, username, password) -> str:
        self.post(url=f'{self.baseUrl}/',
                  _headers={
                      "credentials": "omit",
                      "Content-Type": "application/x-www-form-urlencoded",
                      "Sec-Fetch-User": "?1",
                  },
                  body={
                      'username': username,
                      'password': password,
                      'loginSubmit': 'Login'
                  })

        if not self.validateCreds():
            self.session.cookies.clear()
            raise CredentialsError("Invalid username/password")

        return self.session.cookies.get_dict()

    def validateCreds(self) -> bool:
        return 'access_token' in self.session.cookies.get_dict()
