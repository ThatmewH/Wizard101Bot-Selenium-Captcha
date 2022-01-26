import time
import random
import os
import sys
from selenium.webdriver.common.by import By


class QuestionAnswerer:
    def __init__(self, driver, dictionary_api, correct_answer_pool: dict[str, list],
                 incorrect_answer_pool: dict[str, list]):
        self.driver = driver
        self.dictionary_api = dictionary_api
        self._CORRECT_QUESTIONS = correct_answer_pool
        self._INCORRECT_QUESTIONS = incorrect_answer_pool

    def _get_question(self):
        return self.driver.find_element(By.CLASS_NAME, "quizQuestion").text

    def _get_answers(self):
        while True:
            got_all_answers = True
            time.sleep(3)
            quiz_answers_elems = self.driver.find_elements(By.CLASS_NAME, "answerText")
            quiz_answers = []

            for quiz_answer_elem in quiz_answers_elems:
                quiz_answers.append(quiz_answer_elem.text)

            if len(quiz_answers) == 4:
                for word in quiz_answers:
                    if word == "":
                        got_all_answers = False

            if got_all_answers:
                break

        return quiz_answers

    def _click_answer(self, answer_number):
        check_box_elems = self.driver.find_elements(By.NAME, "checkboxtag")
        check_box_elems[answer_number].click()

    def _next_question(self):
        self.driver.find_element(By.ID, "nextQuestion").click()

    def _calculate_answer(self):
        raise NotImplementedError("Abstract Function. Should Not Be Called")

    def _restart_script(self):
        sys.stdout.flush()
        os.execl(sys.executable, 'python', "C:/Users/thatm/Documents/Python Projects/CaptchaBot/main.py", *sys.argv[1:])

    def answer(self):
        correct_answer = self._calculate_answer()

        while True:
            try:
                self._click_answer(correct_answer)
                self._next_question()
                break
            except (Exception):
                time.sleep(1)

    # Looks for similar words between two sentences
    def _get_similarities(self, given_answers: list, api_answers: list):
        similarities = []

        for given_answer in given_answers:
            max_similarity = 0
            for api_answer in api_answers:
                similarity = 0
                if given_answer != "xxxxxxxxxxxxxxxxxxxxxx":
                    similarity += 1
                for api_word in api_answer.split(" "):
                    for given_word in given_answer.split(" "):
                        if (api_word.__contains__(given_word) or given_word.__contains__(api_word)):
                            similarity += 1
                if similarity > max_similarity:
                    max_similarity = similarity
            similarities.append(max_similarity)

        return similarities

    # Looks for direct answer in api answer. This is more accurate than _get_similarities, but works less often
    def _get_direct_count(self, given_answers: list[str], api_answers: list[str]):
        words_to_add = []
        given_answers += words_to_add

        counts = []

        for given_answer in given_answers:
            max_count = 0
            for api_answer in api_answers:
                count = api_answer.count(given_answer)
                if given_answer != "xxxxxxxxxxxxxxxxxxxxxx":
                    count += 1

                    if given_answer[-1] == "s":
                        count += api_answer.count(given_answer[:-1])

                if count > max_count:
                    max_count = count
            counts.append(max_count)

        return counts

    def get_most_correct_answer(self, given_answers: list[str], api_answers: list[str]):
        direct_counts = self._get_direct_count(given_answers, api_answers)
        highest_count_indexs = self._get_index_of_largest_element(direct_counts)

        similarities = self._get_similarities(given_answers, api_answers)
        highest_similar_indexs = self._get_index_of_largest_element(similarities)

        if highest_count_indexs:
            return random.choice(highest_count_indexs)
        elif highest_similar_indexs:
            return random.choice(highest_similar_indexs)
        else:
            return random.randint(0, 3)

    def _get_index_of_largest_element(self, element_list):
        highest_scored_indexs = []
        highest_simular_score = 0
        for x in range(len(element_list)):
            if element_list[x] == highest_simular_score:
                highest_scored_indexs.append(x)

            elif element_list[x] > highest_simular_score:
                highest_scored_indexs = [x]
                highest_simular_score = element_list[x]

        if highest_simular_score == 0:
            return None

        return highest_scored_indexs

    def _eleminate_answers_with_pool(self, quiz_question, given_answers):
        new_answers = []
        found_correct_answer = False
        if self._CORRECT_QUESTIONS.__contains__(quiz_question):
            if any(x in given_answers for x in self._CORRECT_QUESTIONS[quiz_question]):
                found_correct_answer = True
                for given_answer in given_answers:
                    if self._CORRECT_QUESTIONS[quiz_question].__contains__(given_answer):
                        new_answers.append(given_answer)

                    else:
                        new_answers.append("xxxxxxxxxxxxxxxxxxxxxx")

        if not (found_correct_answer) and self._INCORRECT_QUESTIONS.__contains__(quiz_question):
            for given_answer in given_answers:
                if not (self._INCORRECT_QUESTIONS[quiz_question].__contains__(given_answer)):
                    new_answers.append(given_answer)
                else:
                    new_answers.append("xxxxxxxxxxxxxxxxxxxxxx")

        elif not (found_correct_answer):
            return given_answers

        return new_answers

    def _check_already_got_answer(self, given_answers: list):
        answer_num = 0

        for answer in given_answers:
            if answer != "xxxxxxxxxxxxxxxxxxxxxx":
                answer_num += 1

        if answer_num == 1:
            for x in range(4):
                if given_answers[x] != "xxxxxxxxxxxxxxxxxxxxxx":
                    return x

        return -1



# Answers vocab questions
class VocabAnswerer(QuestionAnswerer):
    def _calculate_answer(self):
        quiz_question = self._get_question()
        given_answers = self._get_answers()

        # Check Question Pool Answer
        given_answers = self._eleminate_answers_with_pool(quiz_question, given_answers)
        if self._check_already_got_answer(given_answers) != -1:
            return self._check_already_got_answer(given_answers)

        # Check API Answer
        given_answers = self.dictionary_api._clean_up_definitions(given_answers)
        api_answers = self.dictionary_api.get_word_definitions(quiz_question)

        correct_answer = self.get_most_correct_answer(given_answers, api_answers)

        return correct_answer


# Answers spelling questions
class SpellingAnswerer(QuestionAnswerer):
    def _calculate_answer(self):
        given_answers = self._get_answers()
        quiz_question = self._get_question()

        given_answers = self._eleminate_answers_with_pool(quiz_question, given_answers)
        if self._check_already_got_answer(given_answers) != -1:
            return self._check_already_got_answer(given_answers)

        for x in range(len(given_answers)):
            if (self.dictionary_api.word_exists(given_answers[x])):
                return x

        return random.randint(0, 3)


class GoogleAnswerer(QuestionAnswerer):
    def _calculate_answer(self):
        quiz_question = self._get_question()
        api_answer = self._get_google_answer(quiz_question)
        self.driver.back()
        self.driver.back()

        given_answers = self._get_answers()

        # Check Question Pool Answer
        given_answers = self._eleminate_answers_with_pool(quiz_question, given_answers)
        if self._check_already_got_answer(given_answers) != -1:
            return self._check_already_got_answer(given_answers)

        given_answers = self.dictionary_api._clean_up_definitions(given_answers)
        correct_answer = self.get_most_correct_answer(given_answers, [api_answer])

        return correct_answer

    def _get_google_answer(self, question: str) -> str:
        self.driver.get("https://www.google.com/")
        search_bar_elem = self.driver.find_element(By.NAME, "q")

        question = self.dictionary_api._clean_up_definitions([question])[0]

        search_bar_elem.send_keys(f"""{question} -wizard101\n""")
        google_answer = ""
        google_answer_elems = self.driver.find_elements(By.CLASS_NAME, "g")

        for ans in google_answer_elems:
            google_answer += ans.text

        google_answer = self.dictionary_api._clean_up_definitions([google_answer])[0]

        return google_answer