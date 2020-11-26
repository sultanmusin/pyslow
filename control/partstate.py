#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"
import time


# Stores integers related to detector parts. Could be mapped to historical database
class PartState:
    RECENT_TIMEOUT = 60 #sec

    def __init__(self, part_type:type):
        self.part_type = part_type
        self.capabilities = part_type.capabilities
        self.volatile = part_type.volatile
        self.state = dict.fromkeys(self.capabilities, None)
        self.last_updated = dict.fromkeys(self.capabilities, None)

    def getState(self, cap:str) ->int:
        if cap not in self.capabilities:
            raise KeyError("PartState.getState: unknown capability %s " % (cap))
        else:
            return self.state[cap]


    def getLastUpdate(self, cap:str) -> float:
        if cap not in self.capabilities:
            raise KeyError("PartState.isRecent: unknown capability %s " % (cap))
        else:
            return self.last_updated[cap]


    def isRecent(self, cap:str) -> bool:
        if cap not in self.capabilities:
            raise KeyError("PartState.isRecent: unknown capability %s " % (cap))
        else:
            la = self.getLastUpdate(cap)
            now = time.time()
            if la is None:
                return False
            else:
                return now - la < PartState.RECENT_TIMEOUT


    def updateState(self, cap:str, value:int, when:float=None):
        timestamp = when if when else time.time()
        if cap not in self.capabilities:
            raise KeyError("PartState.updateState: unknown capability %s " % (cap))
        else:
            self.state[cap] = value
            self.last_updated[cap] = time.time()


    # returns list of all registers that were never updated OR volatile AND not recently updated
    # useful to create a polling command serquence
    def getListToUpdate(self) :   
        return [cap for cap, val in self.state.items() if val is None or cap in self.volatile and not self.isRecent(cap)]
        
