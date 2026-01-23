import tkinter as tk
from tkinter import messagebox
import os
import random
import subprocess
import tempfile

# ---------------- Paths ----------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # where play.py is
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))  # one level up
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
WORDS_FILE = os.path.join(PROJECT_ROOT, "data", "words.txt")
FREQ_FILE = os.path.join(PROJECT_ROOT, "data", "frequency.json")
INFO_FILE = os.path.join(PROJECT_ROOT, "data", "info.json")


# Load words and data
try:
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        WORDS = [w.strip().lower() for w in f if w.strip()]
except Exception as e:
    raise SystemExit(f"Failed to load words file: {e}")

# Java command (adjust classpath if Wordle.class is elsewhere)
JAVA_CMD = ["java", "-cp", os.path.join(SCRIPT_DIR, "src"), "Wordle"]

# ---------------- Java bridge helpers ----------------
def java_hint(remaining_words):
    """Ask Java for the best next guess"""
    if not remaining_words:
        return None

    tmp = None
    src_dir = os.path.join(PROJECT_ROOT, "src")  # Wordle.class lives here
    prev_cwd = os.getcwd()
    os.chdir(src_dir)
    try:
        tmp = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        for w in remaining_words:
            tmp.write(w + "\n")
        tmp.close()

        out = subprocess.check_output(
            ["java", "-cp", ".", "Wordle", "hint", tmp.name,
            WORDS_FILE, FREQ_FILE, INFO_FILE],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()

        return None if out == "NO_WORDS_LEFT" else out.lower()
    except FileNotFoundError:
        messagebox.showerror("Error", "Java or Wordle.class not found.")
        return None
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Java Error", e.output)
        return None
    finally:
        if tmp and os.path.exists(tmp.name):
            os.remove(tmp.name)
        os.chdir(prev_cwd)


# ---------------- Feedback (display only) ----------------
def feedback(secret: str, guess: str) -> str:
    """Local display logic (purely visual)"""
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


# ---------------- GUI ----------------
class WordleTrainer:
    COLORS = {'G': '#6aaa64', 'Y': '#c9b458', 'B': '#787c7e'}

    def __init__(self, master):
        self.master = master
        master.title("Wordle Trainer")
        self.secret = random.choice(WORDS)  # purely for display
        self.remaining = WORDS.copy()
        self.attempts = 0
        self.max_attempts = 6
        self.feedback_boxes = []

        # GUI elements
        self.guess_var = tk.StringVar()
        self.guess_entry = tk.Entry(master, textvariable=self.guess_var, font=("Arial", 24))
        self.guess_entry.grid(row=0, column=0, padx=10, pady=10)
        self.guess_entry.focus()
        self.guess_entry.bind('<Return>', lambda e: self.submit_guess())

        tk.Button(master, text="Submit Guess", command=self.submit_guess).grid(row=0, column=1, padx=10)
        tk.Button(master, text="Hint", command=self.show_hint).grid(row=0, column=2, padx=10)

        self.feedback_frame = tk.Frame(master)
        self.feedback_frame.grid(row=1, column=0, columnspan=3, pady=10)

    def submit_guess(self):
        guess = self.guess_var.get().strip().lower()
        if len(guess) != 5:
            messagebox.showerror("Invalid", "Guess must be exactly 5 letters")
            return
        if guess not in WORDS:
            messagebox.showerror("Invalid", f"'{guess}' is not a valid word")
            return

        self.attempts += 1
        fb = feedback(self.secret, guess)  # visual feedback

        # Display feedback
        row = tk.Frame(self.feedback_frame)
        row.pack(pady=2)
        for i, c in enumerate(fb):
            tk.Label(
                row,
                text=guess[i].upper(),
                bg=self.COLORS[c],
                fg="white" if c != 'B' else "black",
                font=("Arial", 18),
                width=4,
                height=2,
                relief="solid",
                borderwidth=2
            ).pack(side="left", padx=2)
        self.feedback_boxes.append(row)

        # update remaining words using visual feedback
        self.remaining = [w for w in self.remaining if feedback(w, guess) == fb]

        if fb == "GGGGG":
            messagebox.showinfo("Win", f"Solved in {self.attempts} guesses!")
            self.reset_game()
            return

        if not self.remaining:
            messagebox.showinfo("Lose", f"No words remain. Secret was {self.secret.upper()}")
            self.reset_game()
            return

        if self.attempts >= self.max_attempts:
            messagebox.showinfo("Lose", f"Out of attempts. Secret was {self.secret.upper()}")
            self.reset_game()
            return

    def show_hint(self):
        hint = java_hint(self.remaining)
        if hint:
            messagebox.showinfo("Hint", f"Suggested guess: {hint.upper()}")
        else:
            messagebox.showinfo("Hint", "No valid guesses remaining")

    def reset_game(self):
        self.secret = random.choice(WORDS)
        self.remaining = WORDS.copy()
        self.attempts = 0
        self.guess_var.set("")
        for r in self.feedback_boxes:
            r.destroy()
        self.feedback_boxes.clear()


# ---------------- Main ----------------
if __name__ == "__main__":
    root = tk.Tk()
    WordleTrainer(root)
    root.mainloop()
