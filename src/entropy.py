from collections import Counter
import json
import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Example word list (usually all 5-letter words)
WORDS = [w.strip().lower() for w in open('data/words.txt') if w.strip()]

def feedback(secret, guess):
    """
    Return Wordle-style feedback: 'G' = green, 'Y' = yellow, 'B' = black
    """
    secret = list(secret)
    res = ['B'] * 5
    used = [False] * 5

    # Greens
    for i in range(5):
        if guess[i] == secret[i]:
            res[i] = 'G'
            used[i] = True
            secret[i] = None

    # Yellows
    for i in range(5):
        if res[i] == 'G':
            continue
        for j in range(5):
            if not used[j] and guess[i] == secret[j]:
                res[i] = 'Y'
                used[j] = True
                secret[j] = None
                break
    return ''.join(res)

def entropy_for_guess(guess, candidates):
    """
    Compute expected information (entropy) for a guess over all remaining candidates
    """
    pattern_counts = Counter(feedback(w, guess) for w in candidates)
    total = sum(pattern_counts.values())
    H = 0.0
    for count in pattern_counts.values():
        p = count / total
        H -= p * math.log2(p)
    return H

# Compute entropy for each word in WORDS
entropy_scores = {w: entropy_for_guess(w, WORDS) for w in WORDS}

# Print
print("Entropy scores (bits) per word:")
for word, score in entropy_scores.items():
    print(f"{word}: {score:.3f}")

# Save as JSON for later use
with open('data/frequency.json','w') as f:
    json.dump(entropy_scores, f,indent=3)


# this is inspired by https://www.informatica.si/index.php/informatica/article/view/6301