from tkinter import *
from tkinter import messagebox
import words

root = Tk()
word = words.get_word()
print(word)

GREEN = "#007d21"
YELLOW = "#e2e600"
BLACK = "#000000"
WHITE = "#FFFFFF"
GREY = "#5d636b"

root.config(bg=BLACK)
root.geometry("340x320")

guess_num = 0

word_input = Entry(root)
word_input.grid(row=999, column=0, padx=15, pady=20, ipady=8, ipadx=8, columnspan=3)


def getGuess():
    global word
    global guess_num
    guess = word_input.get()

    if len(guess) != 5:
        messagebox.showerror("please use 5 characters", "Please use 5 characters in your guess...")
    else:
        print(guess_num)
        for i, letter in enumerate(guess):
            label = Label(root, text=letter.upper())
            label.grid(row=guess_num, column=i, padx=5, pady=10, ipadx=15, ipady=10)
            if letter == word[i]:
                label.config(bg=GREEN, fg=BLACK)
            elif letter in word and not letter == word[i]:
                label.config(bg=YELLOW, fg=BLACK)
            elif letter not in word:
                label.config(bg=GREY, fg=WHITE)
        if guess == word:
            messagebox.showinfo("correct!", f"Correct! The word was {word}!")
        if guess_num == 4:
            messagebox.showerror("you lose!", f"You Lose! The word was '{word}!'")

        guess_num += 1


word_guess_button = Button(root, text="Guess", command=getGuess)
word_guess_button.grid(row=999, column=3, columnspan=2)

root.mainloop()
