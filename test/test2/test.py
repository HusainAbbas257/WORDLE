#----------------- Add home directory (wordle/) to path----------------------
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# -------------------------- imports ---------------------------------------
import subprocess
import matplotlib.pyplot as plt
import re
# --------------------------------------------------------------------------

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
SRC_DIR = os.path.join(ROOT, 'src')   # contains Wordle.class
RESULT_FILE = os.path.join(os.path.dirname(__file__), 'result.txt')

# -------------------------- run Java solver --------------------------------
print("Running Java Wordle solver... this may take some time")
with open(RESULT_FILE, 'w') as f:
    subprocess.run(
        ["java", "-cp", SRC_DIR, "Wordle"],
        cwd=ROOT,
        stdout=f,
        text=True
    )
print(f"Java solver finished. Results written to {RESULT_FILE}")

# -------------------------- parse Java-style output ------------------------
def parse_java_output(line):
    """
    Converts Java-style {power={-1=24,1=1,...}, time=2.106} to Python dict
    """
    # extract power map
    power_match = re.search(r"power=\{([^}]+)\}", line)
    power = {}
    if power_match:
        items = power_match.group(1).split(",")
        for item in items:
            k, v = item.split("=")
            power[int(k.strip())] = int(v.strip())

    # extract time
    time_match = re.search(r"time=([0-9.]+)", line)
    elapsed_time = float(time_match.group(1)) if time_match else 0.0

    return power, elapsed_time

with open(RESULT_FILE, 'r') as f:
    java_line = f.read().strip()

power, elapsed_time = parse_java_output(java_line)

# -------------------------- plot -------------------------------------------
keys = [1,2,3,4,5,6,-1]
vals = [power[k] for k in keys]

plt.bar([str(k) for k in keys], vals)
plt.xlabel("Attempts (-1 = fail)")
plt.ylabel("Count")
plt.title(f"Wordle bot performance (Time: {elapsed_time:.2f} s)")
plt.show()
