#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations   # For recursive class references

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



import asyncio
import logging
import sys
from functools import partial

sys.path.append('.')
sys.path.append('control')
sys.path.append('lib/hvsys')
sys.path.append('lib/workers')
import config
from message import Message
from detector import *
from hvstatus import * 
from hvsyssupply import HVsysSupply
from worker import Worker



class Proxy(Worker):
    TIMEOUT = 10 #sec

    def __init__(self, detector:Detector, id=None, port_mapping:dict={'*':4001}):
        super().__init__(detector, id)
        self.port_mapping = port_mapping

    def start(self):
        #ports = list(self.port_mapping.values())
        super().start(self.listen)


    async def listen(self):
        pass # TODO

    
    def on_got_command(self, cmd):
        pass # TODO
        


Worker.register_subclass(Proxy)


def handler(loop, context):
    print(context)

def on_alert(msg:str):
    logging.warning(msg)

async def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s')
    configuration = config.load("config/PsdSlowControlConfig.xml", schema="config/PsdSlowControlConfig.xsd")
    detector = Detector(configuration)

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handler)

    try:
        for id, sm in detector.buses.items():
            await asyncio.create_task(sm.connect(), name="Connect to system module")
            asyncio.create_task(sm.send(), name="System module sending loop")
    except OSError as e:
        print("Cannot connect to system module")  

    print("Module link ok")

    proxy = Proxy(detector, '1', on_alert)
    proxy.start()

    if not loop.is_running():
        loop.run_forever() 

    while not proxy.is_done():
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main(), debug=True)
