import tkinter as tk
from src.play import WordleTrainer
from testing import progress as pg
import os
import shutil
import subprocess as sp

def play():
    try:
        print('Starting the play...')
        root = tk.Tk()
        app = WordleTrainer(root)
        root.mainloop()
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
        print('Starting the cheat system...')
        
        sp.run([
            'java','-cp','src','Helper'
        ], check=True)

    except Exception as e:
        print(e)
        return 1
    else:
        return 0
def run():
    '''allows user to use all the features of this project. returns 1 in case of error or exit else 0;'''
    print('''please choose the number of option you want to proceed with:\n\t1-play some Wordle games with helper(or without)\n\t2-view progress of the wordle bot graphically.\n\t3-do a little cheating by asking the bot to help you in today\'s wordle\n\t4-quit''')
    while(True):
        try:
            choice=int(input('your choice, Sir: '))
        except Exception as e:
            print('invalid try again')
            continue
        if(choice in [1,2,3,4]):
            break
        else:
            print('invalid try again')
    match choice:
        case 1:
            return play()
        case 2:
            return prog()
        case 3:
            return cheat()
        case 4:
            print('exiting the programm...')
            return 1
    return 0
if(__name__=='__main__'):
    while run()!=1:
        pass