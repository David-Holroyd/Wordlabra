import random
import pandas as pd
from termcolor import colored

class GuessWord:
    def __init__(self, letters = [], colors = ["white", "white", "white", "white", "white"], count = {}):
        self.letters = letters
        self.colors = colors
        self.count = count

class Wordlabra:
    def __init__(self, letters = [], letras = [], anglicized = [False, False, False, False, False]):
        self.letters = letters
        self.letras = letras
        self.anglicized = anglicized

    def anglicize(self):
        # Converts hispanic symbols to english symbols and adds them to the letters list for comparison with guess
        # It is assumed that user will only input english symbols (no accented letters or ñ)
        cambiar_letras = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ñ': 'N', 'Ó': 'O', 'Ú': 'U'}
        idx = 0
        for sl in self.letras:
            if sl in cambiar_letras.keys():
                self.letters.append(cambiar_letras[sl])
                self.anglicized[self.letras.index(sl)] = True  # Breaks if the are mutliple of the same letter w/ accent
            else:
                self.letters.append(sl)
            idx += 1
        return self

def guess_word(n_rounds):
    # Allows user to guess 5 letters. Does not have to be a valid word
    n_rounds += 1
    guessword = input(f"Please enter guess #{n_rounds}: ").upper()
    while len(guessword) != 5:
        print(f"Please enter a 5 letter word.")
        guessword = input(f"Please enter guess #{n_rounds}: ").upper()
    else:
        pass
    guess_l = []
    for g in guessword:
        guess_l.append(g)
    return guess_l, n_rounds

def check_letters(a, g):
    # This checks the user's guess with the wordlabra answer.
    # If the user guesses the letter in the exact spot, it will be green (and show spanish symbol if necessary)
    # If the user guesses a letter in the wordlabra in the wrong spot, it will be yellow (provided that letter
    # has not already been guessed in correct spot, or guessed more time than it appears in the wordlabra answer)
    # Otherwise, the letter will be white/gray

    hispanicize = {'A':'Á', 'E':'É', 'I':'Í', 'N':'Ñ', 'O':'Ó', 'U':'Ú'}
    g.count = {}

    for i in g.letters:
        g.count[i] = a.letters.count(i)

    for j in range(5):
        if g.letters[j] == a.letters[j]:
            g.colors[j] = "green"
            g.count[g.letters[j]] -= 1
            if a.anglicized[j] and g.letters[j] in hispanicize.keys():
               g.letters[j] = a.letras[j]

    for k in range(5):
        if g.letters[k] in a.letters and g.count[g.letters[k]] > 0:
            g.colors[k] = "yellow"
            g.count[g.letters[k]] -= 1

    print(colored(g.letters[0], g.colors[0]), colored(g.letters[1], g.colors[1]), colored(g.letters[2], g.colors[2]),
          colored(g.letters[3], g.colors[3]), colored(g.letters[4], g.colors[4]))
    return a, g

def play_round(num_rounds_, w_a, w_g):
    # This checks if the wordlabra answer was guessed correctly
    w_a, w_g = check_letters(w_a, w_g)
    if w_g.colors[0] == "green" and w_g.colors[1] == "green" and w_g.colors[2] == "green" and w_g.colors[3] == "green" \
        and w_g.colors[4] == "green":
        print(f"You win! You guessed correctly in {num_rounds_} rounds.")
    else:
        return num_rounds_

# This reads the words/palabras off an excel file and makes a list containing all possible answers
filepath = r'C:\Users\david\Desktop\Excel Stuff\Spanglish.xlsx'
dfs = pd.read_excel(filepath, sheet_name = ['English', 'Español'])
english_df = dfs['English'].values
español_df = dfs['Español'].values
all_wordlabras = []
english_words = english_df.tolist()
español_palabras = español_df.tolist()
for word in english_words:
    all_wordlabras.append(word[0])
for palabra in español_palabras:
    all_wordlabras.append(palabra[0])

# This chooses the wordlabra answer randomly, makes it uppercase, then makes a list containing each letter as an element
num_wls = len(all_wordlabras)
wordlabra_idx = random.randint(0, num_wls-1)
wordlabra = all_wordlabras[wordlabra_idx].upper()
wordlabra_list = []
for l in wordlabra:
    wordlabra_list.append(l)

# Takes user input for guess word, and creates instances of the GuessWord and Wordlabra objects for the 1st guess.
# Coñverts añy español symbols to eñglish :)
num_rounds = 0
guess_list, num_rounds = guess_word(num_rounds)
w_guess = GuessWord(letters= guess_list)
w_answer = Wordlabra(letras=[wordlabra_list[0], wordlabra_list[1], wordlabra_list[2],
                             wordlabra_list[3], wordlabra_list[4]])
w_answer = w_answer.anglicize()
num_rounds = play_round(num_rounds, w_answer, w_guess)

# This loops through the later guesses, until the user runs out of guesses or wins, getting all letters right in 1 guess
while not (w_guess.colors[0] == "green" and w_guess.colors[1] == "green" and w_guess.colors[2] == "green" \
    and w_guess.colors[3] == "green" and w_guess.colors[4] == "green"):
    if num_rounds == 10:
        print(f"You lose! The correct word was {wordlabra}")
        break

    guess_list, num_rounds = guess_word(num_rounds)
    w_guess = GuessWord(guess_list, colors = ["white", "white", "white", "white", "white"])
    num_rounds = play_round(num_rounds, w_answer, w_guess)
















