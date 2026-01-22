# Line chart: accuracy and optimality approaching theoretical limits
import matplotlib.pyplot as plt

# Ordered runs
labels = ["Baseline", "Optimized runtime", "Entropy-based"]
accuracy = [98.9633, 98.9633, 99.44]
average = [3.7438, 3.7438, 3.578]

THEORETICAL_ACCURACY = 100.0
THEORETICAL_AVG = 3.42

x = range(len(labels))

# Accuracy plot
plt.figure()
plt.plot(x, accuracy, marker='o', label="Your accuracy")
plt.axhline(THEORETICAL_ACCURACY, linestyle='--', label="Theoretical max")
plt.xticks(x, labels, rotation=15)
plt.ylabel("Accuracy (%)")
plt.title("Accuracy approaching theoretical maximum")
plt.legend()
plt.show()

# Optimality (average guesses) plot
plt.figure()
plt.plot(x, average, marker='o', label="Your average guesses")
plt.axhline(THEORETICAL_AVG, linestyle='--', label="Theoretical best")
plt.xticks(x, labels, rotation=15)
plt.ylabel("Average guesses")
plt.title("Optimality approaching theoretical minimum")
plt.legend()
plt.show()
