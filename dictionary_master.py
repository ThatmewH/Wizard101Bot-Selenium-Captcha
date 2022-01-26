import requests


class DictionaryAPI:
    def _get_word_data(self, word):
        result = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/" + word)

        return result.text

    def _get_definition_from_data(self, data_text):
        data_text = data_text.replace("definitions", "")
        definitons = []
        while True:
            definition_start_index = data_text.find('definition') + 13
            definition_end_index = data_text.find('"', definition_start_index)
            if (definition_start_index - 13 == -1):
                break
            definitons.append(data_text[definition_start_index:definition_end_index])
            data_text = data_text.replace("definition", "", 1)

        return definitons

    def _clean_up_definitions(self, list_sentences: list):
        _COMMON_WORDS = ["a", "an", "and", "by", "or", "to", "as"
                         , "the", "am", "of", "that", "has", "in", "with", "cause"]

        # Alphabetisize defintions (leave only alphabetical letters in definition)
        for x in range(len(list_sentences)):
            definition_alpha = ""
            for letter in list_sentences[x]:
                if letter.isalpha() or letter.isdigit() or letter == " ":
                    definition_alpha += letter.lower()
                else:
                    definition_alpha += " "
            list_sentences[x] = definition_alpha

        # Remove Common Words
        for x in range(len(list_sentences)):
            new_defintion = ""
            for word in (list_sentences[x].split(" ")):
                if not (_COMMON_WORDS.__contains__(word)):
                    new_defintion += word + " "
            list_sentences[x] = new_defintion[:len(new_defintion) - 1]

        return list_sentences

    def get_word_definitions(self, word):
        word_data = self._get_word_data(word)
        word_definitions = self._get_definition_from_data(word_data)
        word_definitions = self._clean_up_definitions(word_definitions)

        return word_definitions

    def word_exists(self, word):
        word_data = self._get_word_data(word)
        word_definition = self._get_definition_from_data(word_data)

        if word_definition != []:
            return True
        else:
            return False
