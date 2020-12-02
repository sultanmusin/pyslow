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
import config
from hvsys import HVsys
from message import Message 
from task import Task
from partstate import *
from hvsysbus import *



class Detector:
    def __init__(self, config):
        self.buses = {}
        for id, cfg in config.systemModules.items():
            self.buses[id] = HVsysBus(cfg)

        self.config = config

    async def poll_online(self):
        pass

    async def poll_module(self, id):
        module = self.config.modules[id]

        for part in module.parts:
            addr = module.addr[part]
            part_type = HVsys.catalogus[part]
            await self.poll_part(module.systemModuleId, part_type, addr)

    async def poll_module_important(self, id, poll_cb):   # 
        module = self.config.modules[id]
        part = None # TODO 1111111 Get part from some dictionary or whatever

        for part_name in module.parts:
            addr = module.addr[part_name]
            part_type = HVsys.catalogus[part_name]
            await self.poll_part_important(module.systemModuleId, part, addr, poll_cb)

    async def poll_part(self, sys_mod_id, part_type, address):
        capabilities = part_type.capabilities

        for cap in capabilities:
            command = Message(Message.READ_SHORT, address, part_type, cap, 0)
            await self.add_task(sys_mod_id, command, print)


    async def poll_part_important(self, sys_mod_id, part, address, poll_cb):
        important_hv_capabilities = [
        "STATUS",               # status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
        "1/SET_VOLTAGE",
        "2/SET_VOLTAGE",
        "3/SET_VOLTAGE",
        "4/SET_VOLTAGE",
        "5/SET_VOLTAGE",
        "6/SET_VOLTAGE",
        "7/SET_VOLTAGE",
        "8/SET_VOLTAGE",
        "SET_PEDESTAL_VOLTAGE",
        "1/MEAS_VOLTAGE",
        "2/MEAS_VOLTAGE",
        "3/MEAS_VOLTAGE",
        "4/MEAS_VOLTAGE",
        "5/MEAS_VOLTAGE",
        "6/MEAS_VOLTAGE",
        "7/MEAS_VOLTAGE",
        "8/MEAS_VOLTAGE",
        "MEAS_PEDESTAL_VOLTAGE"
        ]
        all_capabilities = part.capabilities

        for cap in all_capabilities:
            if cap in important_hv_capabilities:
                command = Message(Message.READ_SHORT, address, type(part), cap, 0)
                await self.add_task(sys_mod_id, command, partial(poll_cb, part, cap))

    async def add_task(self, sys_mod_id, command, cb):
        await self.buses[sys_mod_id].add_task(command, cb)




