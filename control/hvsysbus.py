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
import sys
import time
from typing import List
from functools import partial

sys.path.append('.')
sys.path.append('lib/hvsys')

from task import *
from partstate import *
from config import *
from hvsys import HVsys
from hvsyssupply import HVsysSupply

class HVsysBus:
    IP_PORT = 4001
    MAX_BURST_COMMANDS = 2
    DefaultBusId = 'default'

    def __init__(self, bus_config, module_configs:list):
        self.id = bus_config.id
        self.port = bus_config.port
        self.task_queue = asyncio.Queue(1000)
        self.timeout = 1.0 # sec
        self.loop = asyncio.get_event_loop()
        self.part_cache = {} # dict[int, PartState]
        self.parts = {} # dict[int, any hvsys part class]

        for mc in module_configs:
            for part_name, part_address in mc.addr.items():   # mc.addr be like {'hv':15, 'led':18}
                part_type = HVsys.catalogus[part_name]        # e.g. HVsysSupply or other part
                if part_address in self.parts:
                    raise ValueError("Duplicate part id = %d for hvsys bus %s" % (part_address, self.id))
                self.parts[part_address] = part_type(bus_config.det_cfg) if part_type == HVsysSupply else part_type()        # now create the instance of the part connected to our bus 

    def getPartCache(self, addr:int, part_type: type) -> PartState:
        if addr not in self.part_cache: 
            self.part_cache[addr] = PartState(part_type)
        
        return self.part_cache[addr]

    def getPart(self, addr:int):
        if addr not in self.parts: 
            raise ValueError("HVsysBus.getPart: invalid part address %s not in config" % (addr))

        return self.parts[addr]


    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.port, HVsysBus.IP_PORT)

    async def disconnect(self):
        self.writer.close()
        logging.info("Disconnecting from system module...")    
        await self.writer.wait_closed()
        logging.info("Done.")    

    async def recv(self, cb, start_time:float):
        logging.debug("recv: wait for line")
        resp = await self.reader.readline()
        logging.debug("recv: line ok")

        logging.debug('%s task success in %.3f sec: %s' % (self.id, time.time()-start_time, resp))    
        #TODO checksum control @ resp[5]
        int_value = int(resp[0:4], 16)
        cb(int_value)

        logging.debug("recv: task done")

    async def send(self):
        logging.debug("send_worker starting")
        while True:
            # Get a "work item" out of the queue.
            #TODO for  MAX_BURST_COMMANDS:
            if not self.task_queue.empty():
                logging.debug("send_worker: get item 1 of %d" % (self.task_queue.qsize()))
                task = await self.task_queue.get()

                message = task.cmd
                # Check cache of the specified part here
                part_cache = self.getPartCache(message.address, message.device)
                if message.is_read_command() and message.capability not in message.device.volatile and part_cache.isRecent(message.capability):
                    response = part_cache.getState(message.capability)
                    logging.info("Found recent value in cache, skipping request! %s/%d/%s == %d"%(message.device.DESCRIPTION, message.address, message.capability, response))
                    task.cb(response)
                else:
                    logging.info("Polling hardware... %s/%d/%s: %s"%(message.device.DESCRIPTION, message.address, message.capability, str(task.cmd).rstrip()))
                    # create a function that will take int and update particular part_cache
                    update_cache_callback = partial(part_cache.updateState, task.part, task.cmd.capability) 
                    # and reqister it to be called after the device responds
                    task.append_cb(update_cache_callback)

                    def update_part_callback(val:str):
                        task.part.state[task.cmd.capability] = val

                    task.append_cb(update_part_callback)

                    self.writer.write(str(task.cmd).encode())
                    try: 
                        await asyncio.wait_for(self.recv(task.cb, task.timestamp), self.timeout)
                    except TimeoutError:
                        logging.warning("No response in timeout=%fs" % (self.timeout))

                    # Notify the queue that the "work item" has been processed.
                    self.task_queue.task_done()
                    logging.debug("send_worker: task done")
            else:
#                print("send_worker: no item")
                await asyncio.sleep(1)
#                print("send_worker: sleep complete")

    async def add_task(self, command, part, cb):
        task = Task(command, part, cb)
        self.task_queue.put_nowait(task)
