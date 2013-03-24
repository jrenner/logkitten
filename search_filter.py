__author__ = 'jrenner'

import re
import logging as log
import constants

class SearchFilter():
    """
    An object that will go through log entries to see if they pass the filter
    """
    # TODO add time filter
    def __init__(self):
        self.pid_min = None
        self.pid_max = None
        self.tag = None
        self.text = None
        self.level = None

    def set_pid_filter(self, low, high=None):
        """
        1 arg -> specific pid
        2 args -> min and max pid numbers
        """
        self.pid_min = low
        if high is None:
            self.pid_max = low
        else:
            self.pid_max = high

    def set_level_filter(self, level):
        if level is None:
            self.level = None
        else:
            for char in level:
                assert(char in constants.LOG_LEVEL)
            assert(len(level) <= 5)
            self.level = level

    def set_tag_filter(self, tag_regex):
        """a regex pattern"""
        self.tag = tag_regex
        tag = r"%s" % tag_regex
        self.tag_re = re.compile(tag, re.IGNORECASE)

    def set_text_filter(self, text_regex):
        """a regex pattern"""
        self.text = text_regex
        text = r"%s" % text_regex
        self.text_re = re.compile(text, re.IGNORECASE)

    def log_filters(self):
        msg = "Filters:\n"
        msg += "\t pid_min: " + str(self.pid_min) + "\n"
        msg += "\t pid_max: " + str(self.pid_max) + "\n"
        msg += "\t tag: " + str(self.tag) + "\n"
        msg += "\t text: " + str(self.text) + "\n"
        msg += "\t level: " + str(self.level) + "\n"
        log.debug(msg)

    def entry_passes_filter(self, entry):
        individual_filters = [
            self.passes_pid_filter,
            self.passes_tag_filter,
            self.passes_text_filter,
            self.passes_level_filter
        ]
        for passes_filter in individual_filters:
            if not passes_filter(entry):
                return False
        return True

    def passes_pid_filter(self, entry):
        if not self.pid_min:
            return True
        low = int(self.pid_min)
        if not self.pid_max:
            high = low
        else:
            high = int(self.pid_max)
        if low <= entry.pid <= high:
            return True
        return False

    def passes_tag_filter(self, entry):
        if not self.tag:
            return True
        found = self.tag_re.search(entry.tag)
        if found:
            return True
        return False

    def passes_text_filter(self, entry):
        if not self.text:
            return True
        found = self.text_re.search(entry.text)
        if found:
            return True
        return False

    def passes_level_filter(self, entry):
        if not self.level:
            return True
        if entry.level in self.level:
            return True
        return False

