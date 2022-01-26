import os
import time

import Wizard101Bot

USERNAME = ""
PASSWORD = ""

class Bot101:
    def __init__(self):
        self.start_url = "https://www.wizard101.com/game/trivia"
        self.selenium_wizard101 = Wizard101Bot.Wizard101Selenium(self.start_url)

    def login_cookies(self):
        self.selenium_wizard101.login_cookies()

    def login_captcha(self):
        self.selenium_wizard101.login_captcha(USERNAME, PASSWORD)

    def start_login(self):
        self._login()
        while not (self.selenium_wizard101.is_logged_in()):
            self._login()

    def _login(self):
        # self.login_cookies()
        # if not (self.selenium_wizard101.is_logged_in()):
        self.login_captcha()
            # self.selenium_wizard101.save_cookies()
        self.selenium_wizard101.driver.refresh()

    def logout(self):
        while (self.selenium_wizard101.is_logged_in()):
            self.selenium_wizard101.driver.get(
                "https://wizard101.com/auth/logout/game?redirectUrl=https%3A%2F%2Fwww.wizard101.com%2Fgame"
            )
            self.selenium_wizard101.driver.refresh()

    def start_answering_quizes(self):
        trivia_urls = [
            "https://www.wizard101.com/quiz/trivia/game/english-trivia",
            "https://www.wizard101.com/quiz/trivia/game/educational-trivia"
        ]
        for url in trivia_urls:
            ready_quizes = self.selenium_wizard101.get_ready_quizes(url)
            for ready_quiz in ready_quizes:

                if ready_quiz.__contains__("Vocabulary"):
                    trivia_type = "vocab"
                elif ready_quiz.__contains__("Spelling") and not(ready_quiz.__contains__("Advanced")):
                    trivia_type = "spelling"
                else:
                    trivia_type = "google"

                remaining_quizes = self.selenium_wizard101.start_trivia(trivia_type, ready_quizes[ready_quiz])

                if remaining_quizes == 0:
                    print("All Quizzes done for the day")
                    return

    def read_last_quiz_time(self):
        file_text = self.selenium_wizard101.read_file("question_pool.txt")
        lines_split = file_text.split("\n")

        last_quiz_time = float(lines_split[2])

        return last_quiz_time

    def check_last_run(self):
        last_quiz_time = self.read_last_quiz_time()
        if time.time() - last_quiz_time < 24 * 60 * 60:
            startup_time = time.strftime('%H:%M', time.localtime(time.time() + (24 * 60 * 60) - (time.time() - last_quiz_time)))
            print(f"Started Early, Starting Back Up At {startup_time}")
            time.sleep((24 * 60 * 60) - (time.time() - last_quiz_time))


while True:
    try:
        bot101 = Bot101()
        bot101.check_last_run()
        bot101.start_login()
        print("Logged in Successfully")
        bot101.start_answering_quizes()
        bot101.logout()
        bot101.selenium_wizard101.write_pool_time()
        time.sleep(24 * 60 * 60 + 60)
    except Exception as e:
        try:
            print("Program Crashed")
            print(e)
            os.remove("cookies.pkl")
        except FileNotFoundError:
            pass
