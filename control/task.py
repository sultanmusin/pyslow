#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



import sys
import time
from typing import Callable
from functools import partial

sys.path.append('.')
sys.path.append('lib/hvsys')
sys.path.append('../lib/hvsys')
from message import Message 

class Task:
    def __init__(self, cmd:Message, cb:Callable[[str], None]):
        self.timestamp = time.time()
        self.cmd = cmd
        self.cb = cb

    # add more listeners to the event of completing the task
    # before the old one...
    def append_cb(self, another_cb:Callable[[str], None]):
        old_cb = self.cb
        def envelope(s:str):
            old_cb(s)
            another_cb(s)

        self.cb = envelope

    #... or after it
    def prepend_cb(self, another_cb:Callable[[str], None]):
        old_cb = self.cb
        def envelope(s:str):
            another_cb(s)
            old_cb(s)

        self.cb = envelope


