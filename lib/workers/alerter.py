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



class Alerter(Worker):
    TIMEOUT = 10 #sec

    def __init__(self, detector:Detector, id=None, callback=None):
        super().__init__(detector, id)
        self.callback = callback

    def start(self):
        super().start(self.poll_online_modules_status)


    async def poll_online_modules_status(self):
        while True:
            for module_id, module_config in self.detector.config.modules.items():
                if module_config.online:
                    logging.debug('poll_online_module_status ' + module_id)
                    address = module_config.address('hv')
                    bus_id = module_config.bus_id
                    #logging.warning("!!! %f"%(self.detector.config.temperature_slope))
                    bus = self.detector.buses[bus_id]
                    part = bus.getPart(address)
                    command = Message(Message.READ_SHORT, address, part, 'STATUS', 0)
                    print("Request: %s"%(str(command).rstrip()))
                    on_complete = partial(self.on_complete_command, part, 'STATUS')
                    asyncio.create_task(self.detector.add_task(bus_id, command, part, on_complete))

            await asyncio.sleep(Alerter.TIMEOUT)

    
    def on_complete_command(self, part, cap, value):
        logging.debug('Alerter: command complete! %s#%s/%s = %s'%(part.DESCRIPTION, "no id", cap, value))
        status = HVStatus(value)
        if status.is_error():
            description = str(status)
            logging.warning(description)
            if self.callback is not None:
                self.callback(description)



Worker.register_subclass(Alerter)


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

    alerter = Alerter(detector, '1', on_alert)
    alerter.start()

    if not loop.is_running():
        loop.run_forever() 

    while not alerter.is_done():
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main(), debug=True)
