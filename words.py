import os.path
import random
import requests

WORD_SITE = "https://www.mit.edu/~ecprice/wordlist.10000"
WORDS_TEXT_FILE = "words.txt"


def get_word():
    is_file = os.path.isfile('words.txt')
    if is_file:
        with open(WORDS_TEXT_FILE, "r") as rf:
            output_words_list = rf.readlines()
            chosen_word = random.choice(output_words_list)
            print(chosen_word)
            return chosen_word
    else:
        with open(WORDS_TEXT_FILE, "w") as wf:
            response = requests.get(WORD_SITE)
            word_list = response.content.splitlines()
            output_words_list = []

            for word in word_list:
                selected = word.decode('utf-8')

                if len(selected) == 5:
                    output_words_list.append(selected)

            for line in output_words_list:
                wf.writelines(f"{line}\n")
    get_word()


get_word()
