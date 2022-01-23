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
from hvsyssupply800c import HVsysSupply800c
from hvsyswall import HVsysWall

class HVsysBus:
    IP_PORT = 4001
    MAX_BURST_COMMANDS = 1
    DefaultBusId = 'default'
    DefaultTimeout = 0.5 # sec

    def __init__(self, bus_config, module_configs:list, detector, global_response_callback=None):
        self.id = bus_config.id
        self.port = bus_config.port
        self.task_queue = asyncio.Queue(10000)
        self.timeout = bus_config.timeout # sec
        self.loop = asyncio.get_event_loop()
        self.part_cache = {} # dict[int, PartState]
        self.parts = {} # dict[int, any hvsys part class]
        self.detector = detector
        self.online = False
        self.module_configs = module_configs
        self.global_response_callback = global_response_callback

        for mc in module_configs:
            for part_name, part_address in mc.addr.items():   # mc.addr be like {'hv':15, 'led':18}
                part_type = HVsys.catalogus[part_name]        # e.g. HVsysSupply or other part
                if part_name == 'hv' and mc.version == 'NA61_2_V2':
                    part_type = HVsysSupply800c               # override default (new) hardware version if the config file says so (for NA61 PSD compatibility)
                elif part_name == 'hv' and mc.version == 'DM64_V2':
                    part_type = HVsysWall                     # override default (new) hardware version if the config file says so (for Wall compatibility)

                if part_address in self.parts:
                    raise ValueError("Duplicate part id = %d for hvsys bus %s" % (part_address, self.id))
                else:
                    if part_type in [HVsysSupply, HVsysSupply800c, HVsysWall] and mc.temperature_from_module not in (mc.id, 'FAKE'):
                        # find the source module
                        bus_id = detector.config.modules[mc.temperature_from_module].bus_id
                        bus = self if bus_id == self.id else self.detector.buses[bus_id]
                        sources = [c for c in bus.module_configs if c.id == mc.temperature_from_module]
                        if len(sources) > 0:
                            address = sources[0].address('hv')
                            mc.temperature_sensor = bus.parts[address]
                            logging.info(f'Setting temperature sensor for module {mc.id} to module {sources[0].id} (bus {bus.id} address {address})')
                    self.parts[part_address] = part_type(mc)        # now create the instance of the part connected to our bus 
                    if mc.online:
                        self.online = True

    def register_global_response_callback(self, cb):
        self.global_response_callback = cb

    def getPartCache(self, addr:int, part_type: type) -> PartState:
        if addr not in self.part_cache: 
            self.part_cache[addr] = PartState(part_type)
        
        return self.part_cache[addr]

    def getPart(self, addr:int):
        if addr not in self.parts: 
            raise ValueError("HVsysBus.getPart: invalid part address %s not in config" % (addr))

        return self.parts[addr]


    async def connect(self):
        fut = asyncio.open_connection(self.port, HVsysBus.IP_PORT)
        try:
            # Wait for 3 seconds, then raise TimeoutError
            self.reader, self.writer = await asyncio.wait_for(fut, timeout=3)
        except asyncio.TimeoutError:
            self.online = False
            logging.warning(f"Cannot connect to {self.port}")

    async def disconnect(self):
        if hasattr(self, 'writer') and self.writer is not None:
            self.writer.close()
            logging.info("Disconnecting from system module...")    
            await self.writer.wait_closed()
            self.writer = None
            logging.info("Done.")    

    async def recv(self, cb, start_time:float):
        logging.debug("recv: wait for line")
        resp = await self.reader.readline()
        logging.debug("recv: line ok")

        logging.debug('%s task success in %.3f sec: %s' % (self.id, time.time()-start_time, resp))    
        #TODO checksum control @ resp[5]
        int_value = int(resp[0:4], 16)
        if self.global_response_callback is not None:
            self.global_response_callback(self, int_value)
        if cb is not None: 
            cb(int_value)

        logging.debug("recv: task done")

    async def send(self):
        logging.debug("send_worker starting")
        while True:
            # Get a "work item" out of the queue.
            #TODO for  MAX_BURST_COMMANDS:
            if not self.task_queue.empty():
                if not self.online:
                    logging.debug("send_worker: bus %s offline, not sending command." % (self.id))
                    await asyncio.sleep(0.1)
                else:
                    logging.debug("send_worker: get item 1 of %d" % (self.task_queue.qsize()))
                    #await asyncio.sleep(0.1)
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

                        task.prepend_cb(update_part_callback)

                        self.writer.write(str(task.cmd).encode())
                        try: 
                            await asyncio.wait_for(self.recv(task.cb, task.timestamp), self.timeout)
                        except asyncio.TimeoutError as e:
                            logging.warning("No response in timeout=%fs" % (self.timeout))
                            if self.global_response_callback is not None:
                                self.global_response_callback(self, None)
    
                        # Notify the queue that the "work item" has been processed.
                        self.task_queue.task_done()
                        logging.debug("send_worker: task done")
            else:
#                print("send_worker: no item")
                await asyncio.sleep(0.1)
#                print("send_worker: sleep complete")

    async def add_task(self, command, part, cb):
        task = Task(command, part, cb)
        self.task_queue.put_nowait(task)

    def queue_length(self):
        return self.task_queue.qsize()
