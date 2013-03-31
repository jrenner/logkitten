__author__ = 'jrenner'

from constants import *
import logging as log
import curses.textpad as textpad
import string

class EditField():
    def __init__(self, y, x, field, width, window, hotkey, accepted_input):
        self.hotkey = hotkey
        self.field = field
        self.y = y
        self.x = x
        self.form_width = width
        self.form_start = x + len(self.get_drawn_field())
        self.form_contents = None
        self.window = window
        self.accepted_input = accepted_input

    def draw(self):
        win = self.window
        win.addstr(self.y, self.x, "(", MAGENTA ^ BOLD)
        win.addstr(self.hotkey.lower(), WHITE ^ BOLD)
        win.addstr(")", MAGENTA ^ BOLD)
        win.addstr(self.field.upper(), WHITE)
        win.addstr(": ", WHITE ^ BOLD)
        if self.form_contents:
            win.addnstr(self.form_contents, self.form_width, CYAN ^ BOLD)

    def get_drawn_field(self):
        # just used to get the length
        return "(%s)" % self.hotkey + self.field.upper() + ":"

    def edit(self):
        self.input_len = 0

        max_y, max_x = self.window.getmaxyx()
        y = max_y / 2
        x = max_x / 2 - (self.form_width / 2)
        border_win = curses.newwin(7, max_x - 4, y - 3, 2)
        border_win.border()
        border_msg = "EDITING " + self.field + ": "
        border_win.addstr(3, 1, border_msg, YELLOW ^ BOLD)
        edit_win = curses.newwin(1, self.form_width + 1, y, 3 + len(border_msg))
        border_win.refresh()
        edit_win.refresh()
        textbox = textpad.Textbox(edit_win)
        self.form_contents = textbox.edit()
        self.form_contents.strip('\n')
        self.validate_form_contents()

    def validate_form_contents(self):
        new_contents = ""
        for char in self.form_contents:
            if char in self.accepted_input:
                new_contents += char
        self.form_contents = new_contents
        if self.accepted_input == LOG_LEVEL:
            # sort the string by alphabet
            self.form_contents = self.form_contents.upper()
            def log_level_key(char):
                levels = "VDIWE"
                return levels.index(char)
            self.form_contents = "".join(sorted(list(self.form_contents),
                                                key=log_level_key))
        if self.form_contents == "":
            self.form_contents = None