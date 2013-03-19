__author__ = 'jrenner'

import re

class SearchFilter():
    """
    An object that will go through log entries to see if they pass the filter
    """
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
        assert type(level) is str
        assert len(level) is 1
        self.level = level

    def set_tag_filter(self, tag_regex):
        """a regex pattern"""
        tag = r"%s" % tag_regex
        self.tag = re.compile(tag)

    def set_text_filter(self, text_regex):
        """a regex pattern"""
        text = r"%s" % text_regex
        self.text = re.compile(text)

    def entry_passes_filter(self, entry):
        assert 'LogEntry' in str(entry.__class__)
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
        if self.pid_min <= entry.pid <= self.pid_max:
            return True
        return False

    def passes_tag_filter(self, entry):
        if not self.tag:
            return True
        found = self.tag.search(entry.tag)
        if found:
            return True
        return False

    def passes_text_filter(self, entry):
        if not self.text:
            return True
        found = self.text.search(entry.text)
        if found:
            return True
        return False

    def passes_level_filter(self, entry):
        if not self.level:
            return True
        if self.level == entry.level:
            return True
        return False

