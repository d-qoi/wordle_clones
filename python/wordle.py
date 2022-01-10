#! /usr/bin/python3

import argparse
import curses
from random import choice
from re import compile
import signal
from sys import exit

stdscr = None  # Global screen

parser = argparse.ArgumentParser(description="A Wordle Clone in Python using Curses")
parser.add_argument(
    "word_list",
    type=argparse.FileType("r"),
    help="A text file with a word per line",
    default="../english-words/words_alpha.txt",
    nargs="?",
)
parser.add_argument("--length", "-l", type=int, help="Length of wordle, defaults to 5", default=5)


def init_curses():
    global stdscr
    stdscr = curses.initscr()
    curses.noecho()  # don't echo keyboard to screen
    curses.cbreak()  # don't wait for enter
    stdscr.keypad(True)  # auto decode non-character keys


def terminate_curses():
    global stdscr
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


def signal_handler(_signum, _frame):
    # terminate_curses()
    exit(0)


class words_dict(object):
    def __init__(self, file, length=5):
        word_list = []
        test = compile(f"^[a-z]{{{length}}}$")
        for line in file:
            word = line.lower().strip()
            if not test.match(word):
                continue
            word_list.append(word)
        print(len(word_list))
        self.word_list = word_list

    def get_next(self):
        return choice(self.word_list)


if __name__ == "__main__":
    # Catch a few signals that might cause curses to lock up and not release the terminal properly
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Then initialize curses
    # init_curses()

    # parse arguments, get word list, pass it to words for processing
    args = parser.parse_args()
    words = words_dict(args.word_list, args.length)
    print(words.get_next())
    print(words.get_next())
