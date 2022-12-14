import os.path
import random
import requests

WORD_SITE = "https://www.mit.edu/~ecprice/wordlist.10000"
WORDS_TEXT_FILE = "words.txt"


def get_word():
    is_file = os.path.isfile(WORDS_TEXT_FILE)
    if is_file:
        with open(WORDS_TEXT_FILE, "r") as rf:
            words = rf.readlines()
    else:
        response = requests.get(WORD_SITE)
        words = response.content.splitlines()
        with open(WORDS_TEXT_FILE, "w") as wf:
            words = [word.decode('utf-8') for word in words if len(word) == 5]
            wf.writelines(f"{line}\n" for line in words)

    chosen_word = random.choice(words)
    return chosen_word


get_word()
