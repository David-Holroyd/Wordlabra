import random
import pandas as pd
from flask import Flask, render_template, flash, request, session

rounds = 1
app = Flask(__name__)
app.secret_key = "wordlabra"


# This reads the words/palabras off my github file and makes a list containing all possible answers, choosing one
def start_game():
    url = r'https://raw.githubusercontent.com/David-Holroyd/Wordlabra/main/spanglish.csv'
    df = pd.read_csv(url, encoding='ISO-8859-1')
    all_wordlabras = df.values.tolist()

    #  This chooses the uppercase wordlabra answer randomly, then makes a list containing each letter as an element
    num_wls = len(all_wordlabras)
    wordlabra_idx = random.randint(0, num_wls - 1)
    wordlabra = all_wordlabras[wordlabra_idx][0].upper()
    w_list = []
    for let in wordlabra:
        w_list.append(let)
    return w_list


wordlabra_list = start_game()
alphabet = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "A", "S", "D", "F", "G", "H", "J", "K", "L",
                    "Z", "X", "C", "V", "B", "N", "M"]


@app.route("/game")
def index():
    session.pop('_flashes', None)
    flash("Try to guess the word in English or Spanish. You have 8 guesses.")
    flash("Please enter your 5 letter guess")
    if request.method == "GET":
        global rounds
        global alphabet
        global wordlabra_list
        rounds = 1
        wordlabra_list = start_game()
        alphabet = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "A", "S", "D", "F", "G", "H", "J", "K", "L",
                    "Z", "X", "C", "V", "B", "N", "M"]
    return render_template("wordlabra_index.html")


@app.route("/play", methods=["POST", "GET"])
def play_wordlabra():
    class GuessWord:
        def __init__(self, letters=[], symbols=["_", "_", "_", "_", "_"], count={}):
            self.letters = letters
            self.symbols = symbols
            self.count = count

    class Wordlabra:
        def __init__(self, letters=[], letras=[], anglicized=[False, False, False, False, False]):
            self.letters = letters
            self.letras = letras
            self.anglicized = anglicized

        def anglicize(self):
            # Converts hispanic symbols to english symbols and adds them to the letters list for comparison with guess
            # It is assumed that user will only input english symbols (no accented letters or ??)
            cambiar_letras = {"??": "A", "??": "E", "??": "I", "??": "N", "??": "O", "??": "U"}
            idx = 0
            for sl in self.letras:
                if sl in cambiar_letras.keys():
                    self.letters.append(cambiar_letras[sl])
                    self.anglicized[self.letras.index(sl)] = True  # Breaks if the are >1 of the same letter w/ accent
                else:
                    self.letters.append(sl)
                idx += 1
            return self

    def guess_word():
        # Allows user to guess 5 letters. Does not have to be a valid word
        global rounds
        rounds += 1 
        flash(f"Please enter guess #{rounds}: ")
        guess_l = []
        if request.method == "POST":
            guessword = request.form.get("user_input")
            while len(guessword) != 5:
                flash(f"Please enter a 5 letter word.")
                guessword = request.form.get("user_input")
            for g in guessword:
                guess_l.append(g.upper())
        else:
            pass
        return guess_l

    def check_letters(a, g):
        # This checks the user's guess with the wordlabra answer.
        # If the user guesses the letter in the exact spot, the symbol will be: *
        # If the user guesses a letter in the wordlabra in the wrong spot, the symbol will be: ^ (provided that letter
        # has not already been guessed in correct spot, or guessed more time than it appears in the wordlabra answer)
        # Otherwise, the symbol will be: _

        hispanicize = {"A": "??", "E": "??", "I": "??", "N": "??", "O": "??", "U": "??"}
        g.count = {}

        for i in g.letters:
            g.count[i] = a.letters.count(i)

        for j in range(5):
            if g.letters[j] == a.letters[j]:
                g.symbols[j] = "*"
                g.count[g.letters[j]] -= 1
                if a.anglicized[j] and g.letters[j] in hispanicize.keys():
                    g.letters[j] = a.letras[j]

        for k in range(5):
            if g.letters[k] in a.letters and g.count[g.letters[k]] > 0:
                if g.symbols[k] == "*":
                    pass
                else:
                    g.symbols[k] = "^"
                    g.count[g.letters[k]] -= 1
            elif g.letters[k] not in a.letters:
                global alphabet
                if g.letters[k] in alphabet:
                    alphabet[alphabet.index(g.letters[k])] = "_"  # This removes the absent letter from list of 
                                                                  # possible letters user will see 
        flash("%s" % " ".join(map(str, g.letters)))
        flash("%s" % " ".join(map(str, g.symbols)))
        flash("%s" % " ".join(map(str, alphabet[:10])))  # This displays the alphabet broken up, like US keyboard
        flash("%s" % " ".join(map(str, alphabet[10:19])))
        flash("%s" % " ".join(map(str, alphabet[19:])))
        return a, g

    def play_round(w_a, w_g):
        # This checks if the wordlabra answer was guessed correctly
        global rounds
        w_a, w_g = check_letters(w_a, w_g)
        if w_g.symbols[0] == "*" and w_g.symbols[1] == "*" and w_g.symbols[2] == "*" and w_g.symbols[3] == "*" and \
                w_g.symbols[4] == "*":
            session.pop("_flashes", None)
            word = ''.join(wordlabra_list)
            flash(f"You win! You guessed the word {word} in {rounds-1} guesses.")  
            flash("Return to /game to play again.")

        else:
            pass

    # Takes user input for guess word, and creates instances of the GuessWord and Wordlabra objects for the 1st guess.
    # Co??verts a??y espa??ol symbols to e??glish :)
    global rounds
    global wordlabra_list
    guess_list = guess_word()
    w_guess = GuessWord(letters=guess_list)
    w_answer = Wordlabra(letras=[wordlabra_list[0], wordlabra_list[1], wordlabra_list[2],
                                 wordlabra_list[3], wordlabra_list[4]])
    w_answer = w_answer.anglicize()

    # This loops through the later guesses, until user runs out of guesses or wins, getting all letters right in 1 guess
    while not (w_guess.symbols[0] == "*" and w_guess.symbols[1] == "*" and w_guess.symbols[2] == "*"
               and w_guess.symbols[3] == "*" and w_guess.symbols[4] == "*"):
        play_round(w_answer, w_guess)
        if rounds > 8:
            flash(f"You lose! The correct word was {wordlabra_list}")
            rounds = 1
            answer = ''.join(wordlabra_list)
            print(answer)
            return render_template("wordlabra_loss.html", answer=answer)
        return render_template("wordlabra_display.html")


if __name__ == '__main__':
    app.run(debug=True)
