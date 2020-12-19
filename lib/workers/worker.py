#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



import asyncio
import logging
import os
import string
import sys

sys.path.append('.')
sys.path.append('lib/hvsys')
sys.path.append('lib/workers')
import config
from message import Message
from detector import *
from hvsyssupply import HVsysSupply



class Worker:
    registry = []
    subclasses = []

    def __init__(self, detector:Detector, id=None):
        self.id = id
        self.detector = detector
        Worker.registry.append(self)
        pass

    def start(self, future):
        try:
            loop = asyncio.get_event_loop()
            self.task = loop.create_task(future(), name=str(self))
        except asyncio.CancelledError:
            pass

    def stop(self):
        self.task.cancel()

    def is_done(self):
        return self.task.done()

    def __str__(self):
        id = self.id if self.id is not None else ""
        return str(type(self)) + '#' + id


    @staticmethod
    def register_subclass(subclass):
        Worker.subclasses.append(subclass)