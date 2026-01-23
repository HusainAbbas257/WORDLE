import tkinter as tk
from src.play import WordleTrainer
from testing import progress as pg
import subprocess as sp
import threading
import os
import sys


def play():
    try:
        print('Starting the play...')
        os.system('python -u \"c:\\Users\\dell\\Desktop\\WORDLE\\src\\play.py\"')
    except Exception as e:
        print(e)
        return 1
    else:
        return 0
def prog():
    try:
        print('Starting the graphs...')
        pg.run()
    except Exception as e:
        print(e)
        return 1
    else:
        return 0

def cheat():
    try:
        sp.run(
            ['java', '-cp', 'src', 'Helper'],
            check=True
        )
    except FileNotFoundError:
        print("Java not found.")
        return 1
    except Exception as e:
        print(e)
        return 1
    return 0


class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Control Panel")
        self.root.geometry("420x360")
        self.root.resizable(False, False)

        self.running = False

        self.container = tk.Frame(root, bg="#0e0e0e")
        self.container.pack(fill="both", expand=True)

        tk.Label(
            self.container,
            text="WORDLE SUITE",
            fg="white",
            bg="#0e0e0e",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=20)

        self.make_button("Play Wordle", self.safe_play)
        self.make_button("View Progress", self.safe_prog)
        self.make_button("Cheat Helper", self.safe_cheat)
        self.make_button("Quit", self.quit_app)

    def make_button(self, text, command):
        btn = tk.Button(
            self.container,
            text=text,
            command=command,
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="white",
            activebackground="#333333",
            activeforeground="white",
            relief="flat",
            width=28,
            height=2
        )
        btn.pack(pady=8)

        # subtle hover animation
        btn.bind("<Enter>", lambda e: btn.config(bg="#2a2a2a"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#1e1e1e"))

    def guard(self):
        if self.running:
            return False
        self.running = True
        self.root.after(100, lambda: setattr(self, "running", False))
        return True

    def threaded(self, func):
        threading.Thread(target=func, daemon=True).start()

    def safe_play(self):
        if self.guard():
            self.threaded(play)

    def safe_prog(self):
        if self.guard():
            self.threaded(prog)

    def safe_cheat(self):
        if self.guard():
            self.threaded(cheat)

    def quit_app(self):
        self.root.destroy()
        sys.exit(0)


def run():
    try:
        root = tk.Tk()
        LauncherGUI(root)
        root.mainloop()
    except Exception as e:
        print(e)
        return 1
    return 0


if __name__ == '__main__':
    run()
