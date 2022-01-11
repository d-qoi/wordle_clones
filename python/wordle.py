#! /usr/bin/python3

import argparse
import curses
from io import FileIO
from random import choice
from re import compile
import signal
from sys import exit
from time import sleep

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
parser.add_argument("--guesses", "-g", type=int, help="Length of wordle, defaults to 6", default=6)


def init_curses():
    global stdscr
    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()  # don't echo keyboard to screen
    curses.cbreak()  # don't wait for enter
    stdscr.keypad(True)  # auto decode non-character keys
    return stdscr


def terminate_curses():
    global stdscr
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


def signal_handler(_signum, _frame):
    terminate_curses()
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

    def check(self, word):
        return word in self.word_list


"""
def wordle(stdscr: curses.window, word_list, length):
    # words = words_dict(word_list, length)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    stdscr.clear()
    winSize = [curses.LINES - 1, curses.COLS - 1]
    playAreaSize = [9, 8, winSize[0] // 2 - 9, winSize[1] // 2 - 4]  # height, width, y, x
    stdscr.addstr(str(winSize))
    stdscr.addstr(str(playAreaSize))
    playArea = stdscr.subwin(*playAreaSize)
    redraw_board(playAreaSize, playArea)
    stdscr.getkey()
"""


class wordle(object):
    QUIT = -1
    NEW = 0
    RESTART = 1
    AWAIT_KEY = 2
    UPDATE_GUESS = 3
    CHECK_GUESS = 4

    def __init__(self, stdscr: curses.window, word_list: FileIO, length: int, guesses: int) -> None:
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.play = True
        self.state = wordle.NEW
        self.screen = stdscr
        self.screen.addstr(b"Welcome to a Knock-off Wordle!\n")
        self.cols = curses.COLS
        self.rows = curses.LINES
        self.words = words_dict(word_list, length)
        self.target = None
        self.current_guess = ""
        self.previous_guesses = []
        self.length = length
        self.guesses = guesses
        self.play_area = [guesses + 2, length + 2, self.rows // 2 - guesses + 2, self.cols // 2 - length // 2]
        self.screen.addstr(f"{str(self.play_area)}")
        self.pa_max_y = self.play_area[0] - 1
        self.pa_max_x = self.play_area[1] - 1
        self.play_screen = self.screen.subwin(*self.play_area)

    def run(self):
        while self.play:
            if self.state == wordle.NEW:
                self.new_game()
            elif self.state == wordle.QUIT:
                self.quit()
            elif self.state == wordle.RESTART:
                self.screen.clear()
                self.redraw_board()
                self.target = self.words.get_next()
                self.state = wordle.AWAIT_KEY
            elif self.state == wordle.AWAIT_KEY:
                key = self.screen.getch()
                # Keys!
                # esc = 27
                # enter = 10
                # backspace = 263
                # down = 258
                # up = 259
                # left = 260
                # right = 261
                if key == 27:
                    self.state = wordle.QUIT
                elif key in range(ord(b"a"), ord("z") + 1) or key in range(ord("A"), ord("Z") + 1):
                    self.last_key = chr(key).lower()
                    self.state = wordle.UPDATE_GUESS
                elif key in [263, 10]:
                    self.last_key = key
                    self.state = wordle.UPDATE_GUESS
            elif self.state == wordle.UPDATE_GUESS:
                self.update_guess()
            else:
                self.state = wordle.NEW
        sleep(50)

    def update_guess(self):
        key = self.last_key
        self.last_key = None
        self.state = wordle.AWAIT_KEY
        if key == 10 and len(self.current_guess) == self.length:
            self.state = wordle.CHECK_GUESS
        elif key == 263 and len(self.current_guess):
            self.current_guess = self.current_guess[:-1]
        elif isinstance(key, str) and len(self.current_guess) < self.length:
            self.current_guess += key
        guess_num = len(self.previous_guesses)
        self.play_screen.addstr(1, guess_num + 1, f"{self.current_guess}{'_'*self.length}"[: self.length])
        self.play_screen.refresh()

    def redraw_board(self):
        self.play_screen.border()
        for y in range(1, self.guesses + 1):
            self.play_screen.addstr(y, 1, "_" * self.length)
        self.play_screen.syncup()

    def new_game(self):
        self.target = None
        self.current_guess = ""
        self.previous_guesses = []
        self.last_key = None
        self.screen.clear()
        self.screen.addstr(1, 1, "Start a new game? (enter for yes, anything else for no.)")
        self.screen.refresh()
        char = self.screen.getch()
        if char != 10:
            self.play = False
        else:
            self.state = wordle.RESTART

    def quit(self):
        self.screen.clear()
        self.screen.addstr(1, 1, "press escape again to quit, anything else to continue")
        self.screen.refresh()
        char = self.screen.getch()
        if char == 27:
            self.play = False
        self.state = wordle.AWAIT_KEY


if __name__ == "__main__":
    # Catch a few signals that might cause curses to lock up and not release the terminal properly
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        stdscr = init_curses()
        args = parser.parse_args()
        game = wordle(stdscr, args.word_list, args.length, args.guesses)
        game.run()
    except Exception as e:
        raise e
    finally:
        terminate_curses()
