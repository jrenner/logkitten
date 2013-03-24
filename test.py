#!/usr/bin/python
__author__ = 'jrenner'

import time

fin = open("test.txt", "r")

data = fin.read()

while True:
    time.sleep(3)
    print "Getting updated data..."
    print fin.read()




