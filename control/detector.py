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
from enum import Enum

sys.path.append('.')
sys.path.append('lib/hvsys')
from config import Config
from hvsys import HVsys
from message import Message 
from task import Task
from partstate import *
from hvsysbus import *
from hvsyssupply import *
from hvsyssupply800c import *



class ModuleState(Enum):
    Offline = 0
    PowerOff = 1
    PowerOn = 2
    Error = 3
    NotReference = 4



class Detector:
    
    def __init__(self, config:Config):
        self.config = config
        self.buses = {} # dict[str,HVsysBus]
        for id, cfg in config.buses.items():
            this_bus_module_configs = [c for c in config.modules.values() if c.bus_id == id]# fetch the list of module connected to certain bus
            self.buses[id] = HVsysBus(cfg, this_bus_module_configs, self)
        
        logging.info("Detector: setting temperature sensors...")
        # As we now have all the buses and their modules populated, we can set the temperature sensors in second pass
        for id, cfg in config.buses.items():
            bus = self.buses[id]
            for part_address, part in bus.parts.items():                
                if type(part) in [HVsysSupply, HVsysSupply800c, HVsysWall] and part.config.temperature_from_module not in (part.config.id, 'FAKE'):
                    # find the sensor module
                    sensor_bus_id = self.config.modules[part.config.temperature_from_module].bus_id
                    sensor_bus = self.buses[sensor_bus_id]
                    sensors = [c for c in sensor_bus.module_configs if c.id == part.config.temperature_from_module]
                    if len(sensors) > 0:
                        address = sensors[0].address('hv')
                        logging.info(f'Setting temperature sensor for module {part.config.id} to module {sensors[0].id} (bus {sensor_bus_id} address {address})')
                        part.set_temperature_sensor(sensor_bus.parts[address])

        logging.info("Done.")


    async def poll_online(self):
        pass

    async def poll_all_status(self, poll_cb):
        for module_config in self.config.modules.values():  # for all modules
            if module_config.online:
                bus = self.buses[module_config.bus_id]     # then we get to which bus it is connected
                if module_config.has('hv'):
                    address = module_config.address('hv')  # get hv part address
                    part = bus.getPart(address)            # get the part object (stored by the bus) 
                    command = Message(Message.READ_SHORT, address, type(part), 'STATUS', 0)
                    await self.add_task(module_config.bus_id, command, part, partial(poll_cb, part, 'STATUS'))

    async def poll_all_temperature(self, poll_cb):
        for module_config in self.config.modules.values():  # for all modules
            if module_config.online:
                bus = self.buses[module_config.bus_id]     # then we get to which bus it is connected
                if module_config.has('hv'):
                    address = module_config.address('hv')  # get hv part address
                    part = bus.getPart(address)            # get the part object (stored by the bus) 
                    command = Message(Message.READ_SHORT, address, type(part), 'TEMPERATURE', 0)
                    await self.add_task(module_config.bus_id, command, part, partial(poll_cb, part, 'TEMPERATURE'))

    async def poll_module(self, id, poll_cb):
        module_config = self.config.modules[id]    # first we get the module config by its id
        bus = self.buses[module_config.bus_id]            # then we get to which bus it is connected

        for part_name in module_config.parts:
            addr = module_config.addr[part_name]   # then we get all of its parts addresses
            part = bus.getPart(addr)               # then for each part we get the part object (stored by the bus) 
            await self.poll_part(module_config.bus_id, part, addr, poll_cb) # and poll the part passing that object for a callback(s)

    # this method is same as above but skips some unimportant registers for speed optimization purposes
    async def poll_module_important(self, id, poll_cb):   # 
        module_config = self.config.modules[id]    # first we get the module config by its id
        bus = self.buses[module_config.bus_id]     # then we get to which bus it is connected

        for part_name in module_config.parts:
            addr = module_config.addr[part_name]   # then we get all of its parts addresses
            part = bus.getPart(addr)               # then for each part we get the part object (stored by the bus) 
            await self.poll_part_important(module_config.bus_id, part, addr, poll_cb) # and poll the part passing that object for a callback(s)

    async def poll_part(self, sys_mod_id, part, address, poll_cb:Callable):
        # priority passengers go first
        all_capabilities = part.priority_capabilities + [p for p in part.capabilities if p not in part.priority_capabilities]

        for cap in all_capabilities:
            command = Message(Message.READ_SHORT, address, type(part), cap, 0)
            await self.add_task(sys_mod_id, command, part, partial(poll_cb, part, cap))


    async def poll_part_important(self, sys_mod_id:str, part, address:int, poll_cb:Callable):
        # temporarily (sic) have a list of important hv registers here (to optimize polling speed skipping the rest)
        important_hv_capabilities = [
        "STATUS",               
        "SET_PEDESTAL_VOLTAGE",
        "1/MEAS_VOLTAGE",
        "2/MEAS_VOLTAGE",
        "3/MEAS_VOLTAGE",
        "4/MEAS_VOLTAGE",
        "5/MEAS_VOLTAGE",
        "6/MEAS_VOLTAGE",
        "7/MEAS_VOLTAGE",
        "8/MEAS_VOLTAGE",
        "9/MEAS_VOLTAGE",
        "10/MEAS_VOLTAGE",
        "MEAS_PEDESTAL_VOLTAGE",
        "TEMPERATURE",
        "VOLTAGE_CALIBRATION",
        "PEDESTAL_VOLTAGE_CALIBRATION", 
        "PEDESTAL_VOLTAGE_CALIBRATION_MIN", 
        "PEDESTAL_VOLTAGE_CALIBRATION_MAX",
        ]
        # priority passengers go first
        all_capabilities = part.priority_capabilities + [p for p in part.capabilities if p not in part.priority_capabilities]
                                                                                                  
        for cap in all_capabilities:
            if type(part) not in [HVsysSupply, HVsysSupply800c] or cap in important_hv_capabilities:
                command = Message(Message.READ_SHORT, address, type(part), cap, 0)
                await self.add_task(sys_mod_id, command, part, partial(poll_cb, part, cap))

    async def monitor_ramp_status(self, bus_id, part, address, callback):
        command = Message(Message.READ_SHORT, address, part, "STATUS", 0)
        for i in range(0,part.config.n_channels):
            await self.add_task(bus_id, command, part, partial(callback, part, i))
            await asyncio.sleep(1)

    def set_hv_state(self, module_id:int, hv_status:int, show_channels:bool):
        error_mask = 65532
        
        #TODO try:
        #    errorMask = getModuleConfigInteger(moduleId, "settings/hv/errorMask");
        #except:
        #    if (Main.verbose == 1) System.out.println("No errorMask found for module: " + moduleId);
            
        state = ModuleState.PowerOff
        if (hv_status & 0x01) != 0:
            state = ModuleState.PowerOn
            if (hv_status & 0x02) != 0:
                if (hv_status & error_mask) != 0 :
                    state = ModuleState.Error
            
    """
        if (showChannels == 1) {
          for(int ch = 0; ch < 10; ch++) {
              int offset = ch + 5;
              if( (hv_status & (1 << offset)) != 0 ) {
                  moduleErrorLabels.get(ch).setText("ERROR:" + hv_status);
              } else{
                  moduleErrorLabels.get(ch).setText("");
              }  
          }
        }
        Main.setModuleState(moduleId, state);
    }
    """

    async def add_task(self, bus_id, command, part, cb):
        await self.buses[bus_id].add_task(command, part, cb)


    def queue_length(self):
        total = 0

        for bus_id in self.buses:
            total = total + self.buses[bus_id].queue_length()

        return total

