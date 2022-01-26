import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SeleniumMaster:
    def __init__(self, start_url: str):
        CHROME_DRIVER_PATH = 'C:/Users/thatm/Documents/chromedriver_win32/chromedriver.exe'

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
        self.start_url = start_url

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open("C:/Users/thatm/Documents/Python Projects/CaptchaBot/question_pool.txt", "wb"))

    def load_cookies(self):
        try:
            cookies = pickle.load(open("C:/Users/thatm/Documents/Python Projects/CaptchaBot/question_pool.txt", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
        except (FileNotFoundError):
            # Cookies does not exist (not a problem)
            pass

    def _enter_login_details(self, username, password):
        # Enter username and password
        username_elem, password_elem = self._get_login_elements()
        username_elem.send_keys(username)
        password_elem.send_keys(password)
        password_elem.submit()

    def _get_login_elements(self):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

    def _get_login_captcha_solver(self):
        raise NotImplementedError("Abstract Function. Should Not Be Called")
