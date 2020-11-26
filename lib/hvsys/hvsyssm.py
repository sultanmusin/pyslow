#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



class HVsysSystemBox:
    cell_id = 0x800e

    DESCRIPTION = "System Box"

    capabilities = {
        "reg0": 0x00,               # Cell ID
        "reg1": 0x02,               # 0000
        "reg2": 0x04,               # 0074
        "reg3": 0x06,               # 0078 
        "reg4": 0x08,               
        "reg5": 0x0a,               
        "reg6": 0x0c,               
        "reg7": 0x0e,               
        "reg8": 0x10,               # 001e
        "reg9": 0x12                # 0046
    }

    capabilities_by_subaddress = {val: key for key, val in capabilities.items()}

    volatile = []


