import time

import selenium_master
import captcha_completers
import dictionary_master
import question_answerers
from selenium.webdriver.common.by import By

class Wizard101Selenium(selenium_master.SeleniumMaster):
    # Starts Login Process with cookies
    def login_cookies(self):
        self.driver.get(self.start_url)
        self.load_cookies()

    # Starts login process with the captcha
    def login_captcha(self, USERNAME: str, PASSWORD: str):
        self.driver.get(self.start_url)
        self._enter_login_details(USERNAME, PASSWORD)
        self._complete_login_hcaptcha("47a7d8db-a257-4257-a9d4-96f75860abae"
                                      , self.driver.current_url)

    def _complete_recaptcha(self, site_key, url):
        recaptcha_completer = _Wizard101ReCaptchaV2Solver(self.driver)
        recaptcha_completer.complete(site_key, url)

    def _complete_login_hcaptcha(self, site_key, url):
        hcaptcha_completer = _Wizard101LoginCaptchaSolver(self.driver)
        hcaptcha_completer.complete(site_key, url)

    def _get_login_elements(self):
        username_elem = self.driver.find_element(By.XPATH,
            "/html/body/div[5]/div[3]/div[1]/dl/dd/ul/li/div/form/div[2]/input")
        password_elem = self.driver.find_element(By.XPATH,
            "/html/body/div[5]/div[3]/div[1]/dl/dd/ul/li/div/form/div[3]/input")
        return username_elem, password_elem

    def is_logged_in(self):
        username_element = self.driver.find_element(By.ID, "userNameOverflow")
        if username_element.text == "Login":
            return False
        return True

    def get_ready_quizes(self, url):
        self.driver.get(url)
        game_elements = self.driver.find_element(By.CLASS_NAME, "gamevert_3column")
        elements = game_elements.find_elements(By.TAG_NAME, "li")

        ready_elements = []
        for element in elements:
            if element.get_attribute("class") != "notake":
                ready_elements.append(element)

        ready_quiz = {}
        for element in ready_elements:
            quiz_name = element.text.split("\n")[0]
            quiz_link = element.find_element(By.TAG_NAME, "a").get_property("href")
            ready_quiz[quiz_name] = quiz_link

        return ready_quiz

    def check_quiz_throttle(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "quizThrottle")
            return True
        except:
            return False

    def _get_answerer_type(self, trivia_type, dictionary_api):
        correct_pool_questions, incorrect_pool_questions, last_quiz_time = self._read_pool_questions()

        if trivia_type == "vocab":
            answerer = question_answerers.VocabAnswerer(self.driver, dictionary_api
                                                        , correct_pool_questions, incorrect_pool_questions)
        elif trivia_type == "spelling":
            answerer = question_answerers.SpellingAnswerer(self.driver, dictionary_api
                                                           , correct_pool_questions, incorrect_pool_questions)
        else:
            answerer = question_answerers.GoogleAnswerer(self.driver, dictionary_api
                                                         , correct_pool_questions, incorrect_pool_questions)

        return answerer

    def start_trivia(self, trivia_type: str, quiz_url):
        print("Answering Trivia Quiz")
        dictionary_api = dictionary_master.DictionaryAPI()
        self.driver.get(quiz_url)

        if self.check_quiz_throttle():
            return 0

        answerer = self._get_answerer_type(trivia_type, dictionary_api)
        while True:
            if self._has_finished_answering():
                break

            answerer.answer()

        self._claim_reward()
        self._log_answers()

    def _has_finished_answering(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "rewardText")
            return True
        except:
            return False

    def _claim_reward(self):
        claim_elem = self.driver.find_element(By.CLASS_NAME, "kiaccountsbuttongreen")
        claim_elem.click()

        self._complete_recaptcha("6LfUFE0UAAAAAGoVniwSC9-MtgxlzzAb5dnr9WWY"
                                 , self.driver.current_url)
        show_answers_elem = self.driver.find_element(By.XPATH,
            "/html/body/div[5]/div[3]/div[2]/div[3]/div[3]/div[3]/table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/div/div/div/div/div/div[3]/div[1]/div[2]/a")
        show_answers_elem.click()

    def _log_answers(self):
        print("Trivia Complete: " + self.driver.find_element(By.CLASS_NAME, "quizScore").text)
        quiz_results_elem = self.driver.find_element(By.ID, "quizResults")
        questions_elems = quiz_results_elem.find_elements(By.TAG_NAME, "div")
        questions_elems.pop(0)

        temp_incorrect_questions = {}
        temp_correct_questions = {}

        for question_elem in questions_elems:
            was_correct, question, answer = self._get_answer_from_quiz_results(question_elem.text)

            if was_correct:
                if (temp_correct_questions.__contains__(question)):
                    temp_correct_questions[question].append(answer)
                else:
                    temp_correct_questions[question] = [answer]
            else:
                if (temp_incorrect_questions.__contains__(question)):
                    temp_incorrect_questions[question].append(answer)
                else:
                    temp_incorrect_questions[question] = [answer]

        correct_pool_questions, incorrect_pool_questions, last_quiz_time = self._read_pool_questions()


        final_incorrect_pool_questions = self.dict_additive_merge(temp_incorrect_questions, incorrect_pool_questions)
        final_correct_pool_questions = self.dict_additive_merge(temp_correct_questions, correct_pool_questions)

        self._write_pool_questions(final_incorrect_pool_questions, final_correct_pool_questions, last_quiz_time)

    def read_file(self, file: str):
        with open(file) as f:
            return f.read()

    def _read_pool_questions(self):
        file_text = self.read_file("C:/Users/thatm/Documents/Python Projects/CaptchaBot/question_pool.txt")
        lines_split = file_text.split("\n")

        incorrect_pool_questions = eval(lines_split[0])
        correct_pool_questions = eval(lines_split[1])
        last_quiz_time = lines_split[2]

        return correct_pool_questions, incorrect_pool_questions, last_quiz_time

    def _write_pool_questions(self, incorrect_pool_questions, correct_pool_questions, last_quiz_time):
        f = open("C:/Users/thatm/Documents/Python Projects/CaptchaBot/question_pool.txt", "w")
        f.write(str(incorrect_pool_questions) + "\n")
        f.write(str(correct_pool_questions) + "\n")
        f.write(last_quiz_time)
        f.close()

    def write_pool_time(self):
        correct_pool_questions, incorrect_pool_questions, last_quiz_time = self._read_pool_questions()
        f = open("C:/Users/thatm/Documents/Python Projects/CaptchaBot/question_pool.txt", "w")
        f.write(str(incorrect_pool_questions) + "\n")
        f.write(str(correct_pool_questions) + "\n")
        f.write(str(time.time()))
        f.close()

    def dict_additive_merge(self, dict1: dict[str, list], dict2: dict[str, list]):
        final_dict = {}
        for key in dict1:
            if dict2.__contains__(key):
                # Add and remove duplicates
                in_first = set(dict1[key])
                in_second = set(dict2[key])
                in_second_but_not_in_first = in_second - in_first
                result = dict1[key] + list(in_second_but_not_in_first)

                final_dict[key] = result
            else:
                final_dict[key] = dict1[key]

        for key in dict2:
            if not (dict1.__contains__(key)):
                final_dict[key] = dict2[key]

        return final_dict

    def _get_answer_from_quiz_results(self, qusetion_result: str):
        question_result_split = qusetion_result.split("Answer: ")

        question = question_result_split[0][question_result_split[0].find(" ") + 1:-1]
        answer_correctness = question_result_split[1]

        if answer_correctness.__contains__("Correct!"):
            return True, question, answer_correctness.replace(" Correct!", "")
        else:
            return False, question, answer_correctness.replace(" Incorrect", "")


class _Wizard101LoginCaptchaSolver(captcha_completers.HCaptchaCompleter):
    def _hcaptcha_go_to_iframe(self):
        # Switch to captcha iframe to get required elements
        frames = self.driver.find_elements(By.TAG_NAME, "iframe")
        self.driver.switch_to.frame(frames[0])

    def _hcaptcha_get_required_elems(self):
        g_elem = self.driver.find_element(By.XPATH,
            '/html/body/table/tbody/tr[2]/td[2]/form/div[3]/div/div[2]/div/div/textarea[2]')
        h_elem = self.driver.find_element(By.XPATH,
            '/html/body/table/tbody/tr[2]/td[2]/form/div[3]/div/div[2]/div/div/textarea[2]')

        return g_elem, h_elem

    def _hcaptcha_inject_token(self, hcaptcha_token, g_elem, h_elem):
        self.driver.execute_script(f"var ele=arguments[0]; ele.innerHTML = '{hcaptcha_token}';", g_elem)
        self.driver.execute_script(f"var ele=arguments[0]; ele.innerHTML = '{hcaptcha_token}';", h_elem)

        self.driver.execute_script(f"setCaptchaInputValue('{hcaptcha_token}');")
        g_elem.submit()


class _Wizard101ReCaptchaV2Solver(captcha_completers.ReCaptchaV2Completer):
    def _recaptchav2_go_to_iframe(self):
        # Switch to captcha iframe to get required elements
        frames = self.driver.find_elements(By.TAG_NAME, "iframe")
        self.driver.switch_to.frame(frames[0])

    def _recaptchav2_inject_token(self, token):
        self.driver.find_element(By.ID, "g-recaptcha-response").innerHTML = token
        self.driver.execute_script(f"reCaptchaCallback('{token}');")
