#!/usr/bin/python
__author__ = 'jrenner'
__version__ = '0.001'

import curses
import sys
import re
import time
import logging as log

log.basicConfig(filename='kitten.log', level=log.DEBUG)

# the baseline reference for this program is gnome-terminal

with open("logs.txt", "r") as logsfile:
    test_cat = logsfile.read()
LOGLINES = test_cat.split('\n')

RE_RAW_TAG = re.compile(r"[VDIWE]/.*\):")
RE_LEVEL = re.compile(r"[VDIWE](?=/)")
RE_TAG = re.compile(r"(?<=[VDIWE]/)[^\(]+")
RE_RAW_PID = re.compile(r"\([ ]*[0-9]+\):")
RE_PID = re.compile(r"[0-9]+")


class LogKitten:


class LogPrinter():
    def __init__(self):
        self.entries = []
        self.color = None

    def addEntry(self, entry):
        assert "LogEntry" in str(entry.__class__)
        self.entries.append(entry)

    def printEntries(self, y, x):
        rows_printed = 0
        base_y, base_x = y, x
        if self.color is None:
            color = WHITE
        else:
            color = self.color
        for entry in self.entries:
            try:
                stdscr.addstr(y, x, "(%6d) " % entry.pid, WHITE ^ BOLD)
                stdscr.addstr(entry.tag, color ^ STANDOUT)
                stdscr.addstr(entry.text, color)
                y += 1
                rows_printed += 1
            except curses.error:
                pass
        return y, x, rows_printed


class LogEntry():
    def __init__(self, log_line):
        raw_tag = RE_RAW_TAG.search(log_line)
        if raw_tag:
            self.tag = RE_TAG.search(raw_tag.group()).group()
            rawPID = RE_RAW_PID.search(raw_tag.group()).group()
            self.pid = int(RE_PID.search(rawPID).group())
            self.text = log_line[len(raw_tag.group()):]
        else:
            self.pid = None
            self.text = None

    def prt(self):
        print "TAG: '%s'\nPID: '%d'\nENTRY: '%s'" % (self.tag, self.pid, self.entry)


def quit(msg=None):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    if msg:
        print "QUIT: " + msg
    else:
        print "QUIT: no message given"
    sys.exit()


def handle_terminal_resize():
    global max_x, max_y
    max_y, max_x = stdscr.getmaxyx()
    stdscr.clear()


def process_input(win):
    global cur_x, cur_y
    cur_y, cur_x = stdscr.getyx()
    c = win.getch()
    if c == -1: # no char returned
        return
    elif c == curses.KEY_RESIZE:  # this is how we detect a terminal resize
        handle_terminal_resize()
    elif c == ord('q') or c == ord('Q'):
        quit("User keyboard exit")
    elif c == curses.KEY_HOME:
        x, y = 0, 0

    # Arrow Keys
    elif c == curses.KEY_UP:
        cur_y -= 1
    elif c == curses.KEY_DOWN:
        cur_y += 1
    elif c == curses.KEY_LEFT:
        cur_x -= 1
    elif c == curses.KEY_RIGHT:
        cur_x += 1


def constrain_yx_to_boundaries(y, x):
    if y < 0:
        y = 0
    elif y >= max_y:
        y = max_y - 1
    if x < 0:
        x = 0
    elif x >= max_x:
        x = max_x - 1
    return y, x


def initialize_colors():
    global BG_COLOR, WHITE, BLACK, RED, BLUE, GREEN, YELLOW, MAGENTA, CYAN
    global BOLD, STANDOUT, UNDERLINE, REVERSE

    # Init colors
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


def process_log(log_level):
    assert type(log_level) == str
    assert len(log_level) == 1
    assert log_level.isupper()
    log = re.findall(r"%s/.*" % log_level, test_cat)
    log_printer = LogPrinter()
    for line in log:
        entry = LogEntry(line)
        if entry.tag != None:
            log_printer.addEntry(entry)
    return log_printer

def test_colors():
    if not curses.has_colors():
        quit("terminal does not support colors")
    colors = [BLACK, WHITE, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN]
    x, y = 4, 0
    test_string = "This is a test of a certain color."
    for color in colors:
        stdscr.addstr(y, x, test_string, color)
        y += 1
        stdscr.addstr(y, x, test_string, color ^ BOLD)
        y += 1
        stdscr.addstr(y, x, test_string, color ^ STANDOUT)
        y += 2
    stdscr.refresh()


def write_log(loglist, color, y, x):
    base_y, base_x = y, x
    for log in loglist:
        stdscr.addstr(y, x, log, color)
        y += 1
    return y, x


def process_logs():
    LOG_VERBOSE = process_log("V")
    LOG_VERBOSE.color = MAGENTA
    LOG_DEBUG = process_log("D")
    LOG_DEBUG.color = GREEN
    LOG_INFO = process_log("I")
    LOG_INFO.color = CYAN
    LOG_WARNING = process_log("W")
    LOG_WARNING.color = YELLOW
    LOG_ERROR = process_log("E")
    LOG_ERROR.color = RED

    return [LOG_VERBOSE, LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR]


def main(wrapped_stdscr):
    global stdscr, max_x, max_y, cur_x, cur_y
    stdscr = wrapped_stdscr
    initialize_colors()
    log_printers = process_logs()
    stdscr.nodelay(1) # don't block on getch()
    max_y, max_x = stdscr.getmaxyx()
    tick_length = 1.0 / 30.0
    cur_y, cur_x = 0, 0
    while True:
        time.sleep(tick_length)
        rows_printed = 0
        process_input(stdscr)
        cur_y, cur_x = constrain_yx_to_boundaries(cur_y, cur_x)
        y, x = 3, 0
        for printer in log_printers:
            y, x, rows_printed = printer.printEntries(y, x, rows_printed)
        stdscr.move(cur_y, cur_x)
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)