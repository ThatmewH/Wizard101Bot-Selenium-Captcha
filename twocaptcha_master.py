from twocaptcha import TwoCaptcha
import requests
import time


class TwoCaptchaMaster:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.solver = TwoCaptcha(self.api_key)

# Use this for captchas like reCaptcha, hCaptcha, anything that needs a token to bypass
class TwoCaptchaTokens(TwoCaptchaMaster):
    def start(self, site_key: str, url: str) -> str:
        request_id = self._get_id(site_key, url)
        request_token = self._get_token(request_id)
        return request_token

    def _get_id(self, site_key: str, url: str) -> str:
        request_id_result = self._request_id(site_key, url)
        result, id = request_id_result.text.split("|")[0], request_id_result.text.split("|")[1]
        if result.lower() != "ok":
            raise NotImplementedError

        return id

    def _get_token(self, request_id: str) -> str:
        while True:
            request_result = requests.get(f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={request_id}")
            if request_result.text == "CAPCHA_NOT_READY":
                time.sleep(6)
            else:
                token = request_result.text.split("|")[1]

                return token

    def _request_id(self, site_key, url):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

class ReCaptchaV2Token(TwoCaptchaTokens):
    def _request_id(self, site_key, url):
        return requests.get(
            f"http://2captcha.com/in.php?key={self.api_key}&method=userrecaptcha&googlekey={site_key}&pageurl={url}"
            )
class HCaptchaToken(TwoCaptchaTokens):
    def _request_id(self, site_key, url):
        return requests.get(
            f"http://2captcha.com/in.php?key={self.api_key}&method=hcaptcha&sitekey={site_key}&pageurl={url}"
        )