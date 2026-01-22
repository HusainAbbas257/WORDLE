import json
from typing import List, Dict


class Wordle:
    def __init__(
        self,
        words_file='data/words.txt',
        freq_file='data/frequency.json',
        info_file='data/info.json'
    ):
        self.SOLUTION: List[str] = []
        self.FREQUENCY: Dict[str, float] = {}
        self.INFO: Dict[str, float] = {}
        self.remaining: List[str] = []
        self.initialize(words_file, freq_file, info_file)

    def initialize(
        self,
        words_file='data/words.txt',
        freq_file='data/frequency.json',
        info_file='data/info.json'
    ):
        # Load solution words
        with open(words_file, 'r') as f:
            self.SOLUTION = [w.strip().lower() for w in f.read().splitlines() if w.strip()]

        # Loading frequency dictionary 
        with open(freq_file, 'r') as f:
            self.FREQUENCY = {k.lower(): v for k, v in json.load(f).items()}

        # Load info dictionary (lowercase keys)
        with open(info_file, 'r') as f:
            self.INFO = {k.lower(): v for k, v in json.load(f).items()}

        # current state
        self.remaining = self.SOLUTION[:]
        self.recompute_available()

    # ---------- helpers ----------
    def recompute_available(self):
        """Recompute availability from remaining words."""
        letters = [set() for _ in range(5)]
        for w in self.remaining:
            for i, ch in enumerate(w):
                letters[i].add(ch)
        self.available = [sorted(list(s)) for s in letters]

    def information(self, s: str) -> float:
        """Sum frequency info of unique letters in a word."""
        info = 0.0
        seen = set()
        for c in s:
            if c not in seen:
                info += self.FREQUENCY.get(c, 0)
                seen.add(c)
        return info

    def isvalid(self, s: str) -> bool:
        """Check if word is in remaining and matches positional availability."""
        if s not in self.remaining:
            return False
        for i, c in enumerate(s):
            if c not in self.available[i]:
                return False
        return True

    # ---------- Wordle feedback ----------
    def feedback(self, secret: str, guess: str) -> str:
        """Return pattern string of length 5 with 'G','Y','B' """
        if secret is None:
            raise TypeError("Did somebody actually called automode without telling the secret word.")

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

    def is_consistent(self, word: str, guess: str, pattern: str) -> bool:
        """Check if 'word' would produce 'pattern' when guessed with 'guess' tbh i just made a one line function idk why."""
        return self.feedback(word, guess) == pattern

    # ---------- state update ----------
    def update(self, guess: str, pattern: str):
        """update remaining based on (guess, pattern) and recompute available."""
        guess = guess.lower()
        pattern = pattern.upper()
        self.remaining = [
            w for w in self.remaining if self.is_consistent(w, guess, pattern)
        ]
        self.recompute_available()

    # ---------- guessing ----------
    def guess(self) -> str:
        """guesses the best word that fits."""
        if not self.remaining:
            return None

        info_scores = {w: self.INFO.get(w, None) for w in self.remaining}
        candidates_with_info = {w: s for w, s in info_scores.items() if s is not None}
        if candidates_with_info:
            return max(candidates_with_info, key=candidates_with_info.get)

        # Fallback 
        best = None
        best_score = (-1, -1.0)
        for w in self.remaining:
            uniq = len(set(w))
            freqsum = sum(self.FREQUENCY.get(c, 0) for c in set(w))
            if (uniq, freqsum) > best_score:
                best_score = (uniq, freqsum)
                best = w
        return best

    # ---------- solver ----------
    def solve(self, secret: str = None, auto: bool = True, verbose: bool = True, max_attempts: int = 6) -> int:
        """
        Play until solved or attempts ended.
        Returns attempts used if solved, else -1.
        """
        # Reset dynamic state
        self.remaining = self.SOLUTION[:]
        self.recompute_available()

        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            g = self.guess()
            if g is None:
                if verbose:
                    print("No valid guess available i guess u lost .")
                return -1

            if verbose:
                print(f"Guess {attempts}: {g}")

            if auto:
                # let it gyess
                if secret is None:
                    raise TypeError("Did somebody actually called automode without telling the secret word.")
                pattern = self.feedback(secret, g)
                if verbose:
                    print(f"Auto feedback: {pattern}")
            else:
                # taking input
                while True:
                    pattern = input("Enter pattern (B/Y/G, length 5): ").strip().upper()
                    if len(pattern) == 5 and all(ch in "BYG" for ch in pattern):
                        break
                    print("Invalid pattern format. Try again.")

            if pattern == "GGGGG":
                if verbose:
                    print(f"Solved in {attempts} attempt(s).")
                return attempts

            prev_len = len(self.remaining)
            self.update(g, pattern)

            if not self.remaining:
                if verbose:
                    print("Feedback is strange so no candidates remain.")
                return -1
            if len(self.remaining) == prev_len and verbose:
                print("No reduction in words so maybe your bot is stupid")

        if verbose:
            print("Attempts ended u lost bro.")
        return -1


if __name__ == "__main__":
    obj = Wordle()
    # Example: auto=False lets you input patterns manually
    print("Result:", obj.solve(auto=False, verbose=True))
