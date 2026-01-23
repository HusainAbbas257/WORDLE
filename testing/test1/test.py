
#----------------- Add home directory (wordle/) to path----------------------
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# --------------------------importing others---------------------------------
# importing others
import matplotlib.pyplot as plt
import time
from src import wordle
# ---------------------------------------------------------------------------


start=time.time()
solver = wordle.Wordle()
words = [w.strip().lower() for w in open('data/words.txt') if w.strip()]

power = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, -1:0}

plt.ion()
fig, ax = plt.subplots()

keys = [1,2,3,4,5,6,-1]

for i, w in enumerate(words, 1):
    at = solver.solve(w, verbose=False)
    power[at] += 1
    solver.initialize()

    ax.clear()
    ax.bar([str(k) for k in keys], [power[k] for k in keys])
    ax.set_title(f"Wordle bot performance ({i}/{len(words)})")
    ax.set_xlabel("Attempts (-1 = fail)")
    ax.set_ylabel("Count")

    plt.pause(0.001)
t=time.time()-start
plt.ioff()
plt.show()

print(power,t)
