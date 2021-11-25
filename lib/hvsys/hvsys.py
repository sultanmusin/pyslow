#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



from hvsysled import HVsysLED
from hvsyssupply import HVsysSupply
from hvsyssupply800c import HVsysSupply800c
from hvsysps import HVsysPS
from hvsyssm import HVsysSystemBox

class HVsys:
    catalogus = {   
        'hv': HVsysSupply,
        'led': HVsysLED,
        'ps': HVsysPS,
        'sm': HVsysSystemBox,
        'hv800c': HVsysSupply800c,
#        'switch': HVsysSwitch
    }

    def find_device_by_cell_id(cell_id: int):
        for (id, device) in HVsys.catalogus.items():
            if device.CELL_ID == cell_id:
                return device
        
        return None

#    @classmethod
#    def GetCapNameBySubaddress(cls, device: type, subaddress: int):
#        if not hasattr(device, "capabilities_by_subaddress"):
#            device.capabilities_by_subaddress = 
#        caps = device.capabilities
#        pass

