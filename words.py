import random
import requests

WORD_SITE = "https://www.mit.edu/~ecprice/wordlist.10000"


def get_word():
    response = requests.get(WORD_SITE)
    word_list = response.content.splitlines()
    output_words_list = []

    for word in word_list:
        selected = word.decode('utf-8')

        if len(selected) == 5:
            output_words_list.append(selected)

    with open("words.txt", "r") as wf:
        output_words_list = wf.readlines()
        chosen_word = random.choice(output_words_list)
        print(chosen_word)
        return chosen_word


get_word()
