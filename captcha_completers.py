import twocaptcha_master

_TWO_CAPTCHA_API = "950150263c83070aaaa80f0f19401cd3"


class CaptchaCompleter:
    def __init__(self, driver):
        self.captcha_type = self.get_captcha_class()
        self.driver = driver

    def complete(self):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

    def get_captcha_class(self):
        raise NotImplementedError("Abstract Function. Should Not Be Called")


class HCaptchaCompleter(CaptchaCompleter):
    def complete(self, site_key: str, url: str):
        # Get captcha token
        hcaptcha_token = self.captcha_type.start(site_key, url)

        self._hcaptcha_go_to_iframe()
        g_elem, h_elem = self._hcaptcha_get_required_elems()
        self._hcaptcha_inject_token(hcaptcha_token, g_elem, h_elem)

    def _hcaptcha_go_to_iframe(self):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

    def _hcaptcha_get_required_elems(self):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

    def _hcaptcha_inject_token(self, hcaptcha_token, g_elem, h_elem):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

    def get_captcha_class(self):
        return twocaptcha_master.HCaptchaToken(_TWO_CAPTCHA_API)

class ReCaptchaV2Completer(CaptchaCompleter):
    def complete(self, site_key: str, url: str):
        token = self.captcha_type.start(site_key, url)
        self._recaptchav2_go_to_iframe()

        self._recaptchav2_inject_token(token)

    def _recaptchav2_go_to_iframe(self):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

    def _recaptchav2_inject_token(self, token):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

    def get_captcha_class(self):
        return twocaptcha_master.ReCaptchaV2Token(_TWO_CAPTCHA_API)