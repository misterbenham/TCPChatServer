import random
import requests


def get_word():
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    word_list = response.content.splitlines()
    output_words_list = []

    for i in range(len(word_list)-1):
        selected = word_list[i].decode('utf-8')

        if "".join(dict.fromkeys(selected)) == selected and len(selected) == 5:

            output_words_list.append(selected)

    chosen_word = random.choice(output_words_list)
    print(chosen_word)
    return chosen_word
