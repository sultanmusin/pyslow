#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



import asyncio
import sys
import time
from functools import partial

sys.path.append('.')
sys.path.append('lib/hvsys')

from task import *
from partstate import *


class HVsysSystemModule:
    IP_PORT = 4001
    MAX_BURST_COMMANDS = 2

    def __init__(self, config):
        #TODO read from cfg
        self.id = config.id
        self.port = config.port
        self.task_queue = asyncio.Queue(1000)
        self.timeout = 1.0 # sec
        self.loop = asyncio.get_event_loop()
        self.part_cache = {}

        #msg = message.Create(message.Message.READ_SHORT, 102, HVsysSupply, "TEMPERATURE", 0)
        #print(msg)
        #task = Task(msg, print)
        #self.task_queue.put_nowait(task)
        #msg = 'r0000x\n'
        #print(msg)
        #task = Task(msg, print)
        #self.task_queue.put_nowait(task)

    def getPartCache(self, addr:int, part_type: type) -> PartState:
        if addr not in self.part_cache: 
            self.part_cache[addr] = PartState(part_type)
        
        return self.part_cache[addr]

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.port, HVsysSystemModule.IP_PORT)

    async def disconnect(self):
        self.writer.close()
        print("Disconnecting from system module...")    
        await self.writer.wait_closed()
        print("Done.")    

    async def recv(self, cb, start_time:float):
        print("recv: wait for line")
        resp = await self.reader.readline()
        print("recv: line ok")

        print('%s task success in %.3f sec: %s' % (self.id, time.time()-start_time, resp))    
        #TODO checksum control @ resp[5]
        int_value = int(resp[0:4], 16)
        cb(int_value)

        print("recv: task done")

    async def send(self):
        print("send_worker starting")
        while True:
            # Get a "work item" out of the queue.
            #TODO for  MAX_BURST_COMMANDS:
            if not self.task_queue.empty():
                print("send_worker: get item 1 of %d" % (self.task_queue.qsize()))
                task = await self.task_queue.get()

                message = task.cmd
                # Check cache of the specified part here
                part_cache = self.getPartCache(message.address, message.device)
                if part_cache.isRecent(message.capability):
                    response = part_cache.getState(message.capability)
                    print("Found recent value in cache, skipping request! %s/%d/%s == %d"%(message.device.DESCRIPTION, message.address, message.capability, response))
                    task.cb(response)
                else:
                    print("No recent value in cache, polling hardware... %s/%d/%s: %s"%(message.device.DESCRIPTION, message.address, message.capability, task.cmd))
                    # create a function that will take int and update particular part_cache
                    update_cache_callback = partial(part_cache.updateState, task.cmd.capability) 
                    # and reqister it to be called after the device responds
                    task.append_cb(update_cache_callback)
                    self.writer.write(str(task.cmd).encode())
                    try: 
                        await asyncio.wait_for(self.recv(task.cb, task.timestamp), self.timeout)
                    except TimeoutError:
                        print("No response in timeout=%fs" % (self.timeout))

                    # Notify the queue that the "work item" has been processed.
                    self.task_queue.task_done()
                    print("send_worker: task done")
            else:
#                print("send_worker: no item")
                await asyncio.sleep(1)
#                print("send_worker: sleep complete")

    async def add_task(self, command, cb):
        task = Task(command,cb)
        self.task_queue.put_nowait(task)
