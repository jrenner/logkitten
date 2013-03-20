#!/usr/bin/python
__author__ = 'jrenner'
__version__ = '0.001'

import sys
import re
import curses
import textwrap
import time
import logging as log


log.basicConfig(filename='kitten.log', filemode="w", level=log.DEBUG)

# the baseline reference for this program is gnome-terminal

with open("logs.txt", "r") as logsfile:
    test_cat = logsfile.read()
LOGLINES = test_cat.split('\n')
FIRST_ROW_AT = 5

editing_field = None

# define regex
RE_RAW_TAG = re.compile(r"[VDIWE]/.*\):")
RE_LEVEL = re.compile(r"[VDIWE](?=/)")
RE_TAG = re.compile(r"(?<=[VDIWE]/)[^\(]+")
RE_RAW_PID = re.compile(r"\([ ]*[0-9]+\):")
RE_PID = re.compile(r"[0-9]+")

#### globals
num_rows_to_print = 0 # automatically set based on terminal height later
skip_to_row = 0
edit_fields = {}


class LogKitten():
    def __init__(self):
        self.log_holders = []
        self.process_logs()

    def add_LogHolder(self, log_holder):
        assert('LogHolder' in str(log_holder.__class__))
        self.log_holders.append(log_holder)

    def process_logs(self):
        self.add_LogHolder(process_log())

    def count_all_entries(self):
        count = 0
        for log_holder in self.log_holders:
            count += len(log_holder.entries)
        return count

    def print_logs(self, y, x, filter=None):
        """
        This prints everything we have
        """
        base_x = x
        rows_printed = 0 - skip_to_row
        for log_holder in self.log_holders:
            if rows_printed < num_rows_to_print:
                y, x, rows_printed =\
                    log_holder.print_entries(y, base_x, rows_printed, filter)
        return y, x


class LogHolder():
    def __init__(self):
        self.entries = []
        self.colors = {'V': MAGENTA,
                       'D': GREEN,
                       'I': CYAN,
                       'W': YELLOW,
                       'E': RED}

    def add_entry(self, entry):
        assert "LogEntry" in str(entry.__class__)
        self.entries.append(entry)

    def print_entries(self, y, x, rows_printed, filter=None):
        base_y, base_x = y, x
        for entry in self.entries:
            if filter:
                if not filter.entry_passes_filter(entry):
                    continue  # does not meet filter requirements
            if rows_printed < 0:
                rows_printed += 1
            elif rows_printed < num_rows_to_print:
                color = self.colors[entry.level]
                try:
                    x = base_x
                    old_y = y
                    row_text = "{:<5}".format("%d " %
                                             (rows_printed + skip_to_row))
                    stdscr.addstr(y, x, row_text, BLUE ^ BOLD)
                    pid_text = "{:<5}".format("%d" % entry.pid)
                    stdscr.addstr(pid_text, WHITE ^ BOLD)
                    stdscr.addstr(entry.tag, color ^ STANDOUT)
                    y, x = stdscr.getyx()
                    width = (max_x - 1) - x
                    text_lines = textwrap.wrap(entry.text, width,
                        subsequent_indent = "    ")
                    for line in text_lines:
                        stdscr.addstr(y, x, line, color)
                        y += 1
                    rows_printed += y - old_y
                except curses.error, e:
                    quit("curses.error at xy(%d, %d): " % (x, y) + str(e))
        return y, x, rows_printed


class LogEntry():
    def __init__(self, log_line):
        raw_tag = RE_RAW_TAG.search(log_line)
        if raw_tag:
            rawPID = RE_RAW_PID.search(raw_tag.group()).group()
            self.tag = RE_TAG.search(raw_tag.group()).group()
            self.pid = int(RE_PID.search(rawPID).group())
            # text = everything after tag + pid
            self.text = log_line[len(raw_tag.group()):]
            self.level = RE_LEVEL.search(raw_tag.group()).group()
            #log.info("\n" + str(self) + "\n")
        else:
            self.tag = None
            self.pid = None
            self.text = None
            self.level = None

    def is_valid(self):
        for item in [self.tag, self.pid, self.text, self.level]:
            if item is None:
                return False

    def __str__(self):
        return "LEVEL: '%s'\nTAG: '%s'\nPID: '%d'\nENTRY: '%s'" % (self.level,
                self.tag, self.pid, self.text)


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


def process_input(win):
    global cur_x, cur_y, editing_field
    c = win.getch()
    if c == -1: # no char returned
        return
    elif c == curses.KEY_RESIZE:  # this is how we detect a terminal resize
        handle_terminal_resize()
        stdscr.clear()
    elif c == ord('q') or c == ord('Q'):
        quit("User keyboard exit")
    elif c == curses.KEY_HOME:
        x, y = 0, 0
    elif c == curses.KEY_PPAGE: # page up
        skip_page('up')
    elif c == curses.KEY_NPAGE: # page down
        skip_page('down')
    # Arrow Keys
    elif c == curses.KEY_UP:
        cur_y -= 1
    elif c == curses.KEY_DOWN:
        cur_y += 1
    elif c == curses.KEY_LEFT:
        cur_x -= 1
    elif c == curses.KEY_RIGHT:
        cur_x += 1
    # edit texts
    else:
        for edit_field in edit_fields.values():
            if 0 <= c < 256:
                if chr(c).lower() == edit_field.hotkey.lower():
                    edit_field.edit()
                    stdscr.clear()




def skip_page(direction):
    global skip_to_row
    step = 10
    if direction == 'up':
        step *= -1
    if (skip_to_row + step >= 0):
        skip_to_row += step
        stdscr.clear()


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


def process_log():
    log = re.findall(r"[VDIWE]/.*", test_cat)
    log_holder = LogHolder()
    for line in log:
        entry = LogEntry(line)
        if entry.tag:
            log_holder.add_entry(entry)
    return log_holder


def get_number_of_rows_to_print():
    return max_y - 7


def main(wrapped_stdscr):

    # initialization
    global stdscr, max_x, max_y, cur_x, cur_y, num_rows_to_print, filter
    global editing_field
    stdscr = wrapped_stdscr
    stdscr.nodelay(1) # don't block on getch()
    max_y, max_x = stdscr.getmaxyx()
    tick_length = 1.0 / 60.0
    cur_y, cur_x = 0, 0
    kitten = LogKitten()
    filter = SearchFilter()

    edit_fields['pid_min'] = EditField(1, 0, 'pid_min', 5, stdscr, 'm',
                                       NUMERICAL)
    edit_fields['pid_max'] = EditField(1, 30, 'pid_max', 5, stdscr, 'x',
                                       NUMERICAL)
    edit_fields['tag'] = EditField(2, 0, 'tag', 24, stdscr, 'g',
                                   TEXTUAL)
    edit_fields['level'] = EditField(2, 30, 'level', 1, stdscr, 'l',
                                     LOG_LEVEL)
    edit_fields['text'] = EditField(3, 0, 'text', 24, stdscr, 't',
                                    TEXTUAL)


    while True:
        start_time = time.time()
        num_rows_to_print = get_number_of_rows_to_print()
        time.sleep(tick_length)
        process_input(stdscr)
        cur_y, cur_x = constrain_yx_to_boundaries(cur_y, cur_x)
        first_row = skip_to_row
        last_row = skip_to_row + num_rows_to_print
        stdscr.addstr(0, 0, "Unfiltered entries: %d, showing: %d -> %d" %
                     (kitten.count_all_entries(), first_row, last_row), WHITE)
        stdscr.addstr(1, 0, "Filter -- ", BLUE ^ BOLD)
        for edit in edit_fields.values():
            edit.draw()
        y, x = FIRST_ROW_AT, 0

        #filter
        pid_min = edit_fields['pid_min'].form_contents
        pid_max = edit_fields['pid_max'].form_contents
        filter.set_pid_filter(pid_min, pid_max)
        filter.set_level_filter(edit_fields['level'].form_contents)
        filter.set_tag_filter(edit_fields['tag'].form_contents)
        filter.set_text_filter(edit_fields['text'].form_contents)
        #filter.log_filters()

        kitten.print_logs(y, x, filter)
        stdscr.move(cur_y, cur_x)
        stdscr.refresh()
        #log.debug("main loop time: %.3f seconds" % (time.time() - start_time))

if __name__ == "__main__":
    curses.initscr()
    curses.start_color()
    from constants import *
    from search_filter import SearchFilter
    from edit_field import EditField
    curses.wrapper(main)