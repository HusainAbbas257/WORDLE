"""issue: there is a problem that it remakes all that things by itself insead of using Wordle.java for simplicity."""



import tkinter as tk
from tkinter import messagebox
import random
import os
import json
from collections import defaultdict

# Paths
ROOT = os.path.abspath(".")
DATA_DIR = os.path.join(ROOT, "data")
WORDS_FILE = os.path.join(DATA_DIR, "words.txt")
FREQ_FILE = os.path.join(DATA_DIR, "frequency.json")
INFO_FILE = os.path.join(DATA_DIR, "info.json")

# Load words and data
try:
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        WORDS = [w.strip().lower() for w in f if w.strip()]
except Exception as e:
    raise SystemExit(f"Failed to load words file: {e}")

try:
    with open(FREQ_FILE, "r", encoding="utf-8") as f:
        FREQUENCY = {k.lower(): float(v) for k, v in json.load(f).items()}
except Exception:
    # fallback empty
    FREQUENCY = {}

try:
    with open(INFO_FILE, "r", encoding="utf-8") as f:
        INFO = {k.lower(): float(v) for k, v in json.load(f).items()}
except Exception:
    INFO = {}


# Utility: Wordle feedback exactly matching the Java logic
def feedback(secret: str, guess: str) -> str:
    secret = secret.lower()
    guess = guess.lower()
    res = ['B'] * 5
    used = [False] * 5

    # Greens
    for i in range(5):
        if guess[i] == secret[i]:
            res[i] = 'G'
            used[i] = True

    # Yellows
    for i in range(5):
        if res[i] == 'G':
            continue
        for j in range(5):
            if not used[j] and guess[i] == secret[j]:
                res[i] = 'Y'
                used[j] = True
                break

    return ''.join(res)


# Entropy calculation (same logic as Entropy.java)
def log2(x: float) -> float:
    import math
    return math.log(x) / math.log(2)


def entropy_for_guess(guess: str, remaining: list) -> float:
    # pattern -> count
    pattern_count = defaultdict(int)
    for secret in remaining:
        p = feedback(secret, guess)
        pattern_count[p] += 1
    total = len(remaining)
    H = 0.0
    for count in pattern_count.values():
        p = count / total
        H -= p * log2(p)
    return H


class WordleTrainer:
    COLORS = {'G': '#6aaa64', 'Y': '#c9b458', 'B': '#787c7e'}

    def __init__(self, master):
        self.master = master
        master.title("Wordle Trainer")

        self.reset_state()

        self.guess_var = tk.StringVar()
        self.guess_entry = tk.Entry(master, textvariable=self.guess_var, font=("Arial", 24))
        self.guess_entry.grid(row=0, column=0, padx=10, pady=10)
        self.guess_entry.focus()
        self.guess_entry.bind('<Return>', lambda e: self.submit_guess())

        self.submit_btn = tk.Button(master, text="Submit Guess", command=self.submit_guess)
        self.submit_btn.grid(row=0, column=1, padx=10, pady=10)

        self.hint_btn = tk.Button(master, text="Hint", command=self.show_hint)
        self.hint_btn.grid(row=0, column=2, padx=10, pady=10)

        self.feedback_frame = tk.Frame(master)
        self.feedback_frame.grid(row=1, column=0, columnspan=3, pady=10)

        self.feedback_boxes = []

    def reset_state(self):
        self.secret = random.choice(WORDS)
        self.attempts = 0
        self.max_attempts = 6
        self.remaining = WORDS.copy()
        self.recompute_available()

    def recompute_available(self):
        # not required for GUI but keep parity with Java
        letters = [set() for _ in range(5)]
        for w in self.remaining:
            for i in range(5):
                letters[i].add(w[i])
        self.available = [sorted(list(s)) for s in letters]

    def is_consistent(self, word: str, guess: str, pattern: str) -> bool:
        return feedback(word, guess) == pattern

    def submit_guess(self):
        guess = self.guess_var.get().strip().lower()
        if len(guess) != 5 or guess not in WORDS:
            messagebox.showerror("Invalid", "Guess must be a valid 5-letter word")
            return

        self.attempts += 1
        fb = feedback(self.secret, guess)

        # Display colored feedback
        row_frame = tk.Frame(self.feedback_frame)
        row_frame.pack(pady=2)
        for i, c in enumerate(fb):
            lbl = tk.Label(row_frame, text=guess[i].upper(), bg=self.COLORS[c],
                           fg='white' if c != 'B' else 'black', font=("Arial", 18),
                           width=4, height=2, borderwidth=2, relief="solid")
            lbl.pack(side='left', padx=2)
        self.feedback_boxes.append(row_frame)

        if fb == "GGGGG":
            messagebox.showinfo("Win", f"Correct! The word was '{self.secret.upper()}' in {self.attempts} guesses.")
            self.reset_game()
            return

        # update remaining words using the (guess, pattern)
        prev = len(self.remaining)
        self.remaining = [w for w in self.remaining if self.is_consistent(w, guess, fb)]
        self.recompute_available()

        if not self.remaining:
            messagebox.showinfo("Lose", f"No words remain — inconsistent feedback. The secret was '{self.secret.upper()}'")
            self.reset_game()
            return

        if self.attempts >= self.max_attempts:
            messagebox.showinfo("Lose", f"You ran out of attempts! The word was '{self.secret.upper()}'")
            self.reset_game()
            return

        if len(self.remaining) == prev:
            # no reduction
            print("No reduction in words so maybe your input was inconsistent")

    def show_hint(self):
        hint = self.get_best_guess()
        messagebox.showinfo("Hint", f"Suggested best guess: {hint.upper()}" if hint else "No words remaining")

    def get_best_guess(self):
        # follow the Java logic: if remaining <= 500, use entropy over remaining guesses
        rem = self.remaining
        if not rem:
            return None

        if len(rem) <= 500:
            best_entropy = -1.0
            best_word = None
            # compute entropy for each candidate in rem
            for guess in rem:
                e = entropy_for_guess(guess, rem)
                if e > best_entropy:
                    best_entropy = e
                    best_word = guess
            if best_word:
                return best_word

        # fallback: pick highest INFO value which is precomputed
        best_info = None
        best_val = -1.0
        for w in rem:
            v = INFO.get(w)
            if v is not None and v > best_val:
                best_val = v
                best_info = w
        if best_info:
            return best_info

        # last fallback: maximize unique letters and then frequency sum
        best = None
        best_uniq = -1
        best_freq = -1.0
        for w in rem:
            uniq = len(set(w))
            freqsum = sum(FREQUENCY.get(ch, 0.0) for ch in set(w))
            if uniq > best_uniq or (uniq == best_uniq and freqsum > best_freq):
                best_uniq = uniq
                best_freq = freqsum
                best = w
        return best

    def reset_game(self):
        self.reset_state()
        self.guess_var.set("")
        for row in self.feedback_boxes:
            row.destroy()
        self.feedback_boxes.clear()


if __name__ == "__main__":
    root = tk.Tk()
    app = WordleTrainer(root)
    root.mainloop()
