__author__ = 'jrenner'

import curses
from string import digits, letters, punctuation

BG_COLOR = curses.COLOR_BLACK
curses.init_pair(1, curses.COLOR_WHITE, BG_COLOR)
curses.init_pair(2, curses.COLOR_BLACK, BG_COLOR)
curses.init_pair(3, curses.COLOR_RED, BG_COLOR)
curses.init_pair(4, curses.COLOR_GREEN, BG_COLOR)
curses.init_pair(5, curses.COLOR_BLUE, BG_COLOR)
curses.init_pair(6, curses.COLOR_YELLOW, BG_COLOR)
curses.init_pair(7, curses.COLOR_MAGENTA, BG_COLOR)
curses.init_pair(8, curses.COLOR_CYAN, BG_COLOR)

# Assign colors
WHITE = curses.color_pair(1)
BLACK = curses.color_pair(2)
RED = curses.color_pair(3)
GREEN = curses.color_pair(4)
BLUE = curses.color_pair(5)
YELLOW = curses.color_pair(6)
MAGENTA = curses.color_pair(7)
CYAN = curses.color_pair(8)

BOLD = curses.A_BOLD
STANDOUT = curses.A_STANDOUT
UNDERLINE = curses.A_UNDERLINE
REVERSE = curses.A_REVERSE

NUMERICAL = digits
TEXTUAL = letters + punctuation + digits
LOG_LEVEL = "VDWIEvdwie"