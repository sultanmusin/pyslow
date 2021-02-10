#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"


import logging
import sys

sys.path.append('.')
sys.path.append('control')
sys.path.append('lib/hvsys')
sys.path.append('lib/workers')
import config
from message import Message
from detector import *
from hvsyssupply import HVsysSupply


# Module status register: 
# X3 E10 E9 E8 E7 E6 E5 E4 E3 E2 E1 X3 X3 RAMP E ON
# X3 = reserved
# En = Error on channel 3
# E = Any error
# ON = HV is on

class HVStatus:
    N_CHANNELS = 10 
    OFFSET_ON = 0
    OFFSET_ERROR = 1
    OFFSET_RAMP = 2
    OFFSET_ERROR_CHANNEL = {ch:ch+4 for ch in range(1,1 + N_CHANNELS)}  # for 1-based channel number

    def __init__(self, status_register:int):
        self.status = status_register

    def is_on(self): 
        return self.check_bit(HVStatus.OFFSET_ON)
    
    def is_error(self): 
        return self.check_bit(HVStatus.OFFSET_ERROR) and self.check_bit(HVStatus.OFFSET_ON) # when it is off the error flag is also always on

    def is_ramp(self):
        return self.check_bit(HVStatus.OFFSET_RAMP)

    def is_error_on_channel(self, ch:int): # 1-based
        if ch not in HVStatus.OFFSET_ERROR_CHANNEL:
            raise ValueError("HVStatus: unknown offset for channel " + ch)
        return self.check_bit(HVStatus.OFFSET_ERROR_CHANNEL[ch])
    
    def check_bit(self, offset):
        return self.status & (1 << offset) != 0

    def __str__(self):
        if self.is_on():
            result = "HV ON"
            if self.is_error():
                result += "; ERROR on channels "
                error_list = []
                for ch in HVStatus.OFFSET_ERROR_CHANNEL.keys():
                    if self.is_error_on_channel(ch):
                        error_list.append(str(ch))
                result += ','.join(error_list)
            return result
        else:
            return "HV OFF"

    def channel_description(self, ch:int):
        if ch < 1 or ch > HVStatus.N_CHANNELS:
            return "unknown channel"
        elif self.is_error_on_channel(ch):
            return "ERROR"
        elif self.is_on() and self.is_ramp():
            return "Ramp Up"
        elif self.is_on() and not self.is_ramp():
            return "HV ON"
        elif not self.is_on() and self.is_ramp():
            return "Ramp Down"
        elif not self.is_on() and not self.is_ramp():
            return "HV OFF"

            