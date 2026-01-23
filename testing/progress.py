# Line chart: accuracy and optimality approaching theoretical limits
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")  # ensures matplotlib uses Tkinter safely

def run():
    print('Here is the the vast progress done by my wordle bot')
    # Ordered runs
    labels = ["Baseline v1", "Optimized runtime v2", "Entropy-based v3"]
    accuracy = [98.9633, 98.9633, 99.44]
    average = [3.7438, 3.7438, 3.578]
    time=[834.9751560688019 ,1.805,3.578]

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
    
    # time plot
    plt.figure()
    plt.plot(x, time, marker='o', label="Your time to solve or all words")
    plt.xticks(x, labels, rotation=15)
    plt.ylabel("Average time")
    plt.legend()
    plt.show()
    print("Thank you\nFor more information please check out the test folder")


if __name__=='__main__':
    run()