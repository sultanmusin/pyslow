#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"

#import sys
#sys.path.append('control')
#from config import Config

class HVsysLED:
    cell_id = 0x8006

    DESCRIPTION = "LED Driver"

    capabilities = {
        "STATUS": 0x00, #               # status -  error i.e. in process of settings - stat=avADC-ADCsetpt, #
        "AUTOREG": 0x02, #              # autoreg - 1 - cell will autoregulate LED output to keep ADC readings at ADCsetpt
        "SET_FREQUENCY": 0x04, #                 # 2 freq - generator frequency (Hz)
                                        # remember freq in range (1-1000) -> internal gen; freq out of range (1-1000) (for example -1 from TCL) -> external gen/sync. IF freq=0 -> LED disabled
                                        # should be 0 for normal triggered operation
        "AVERAGE_POINTS": 0x06,         # number of adc measurement points to average in regulation process
        "SET_AMPLITUDE": 0x08,              # 4 DACval - will be written to LED DAC
        "ADC_SET_POINT": 0x0a,          # 5 PIN ADC setpt - cell will autoregulate LED output to keep ADC readings at ADCsetpt
        "CELL_ID": 0x0c,                # 6 new cell ID
        "AVERAGE_ADC": 0x0e,            # 7 avADC - averaged ADC readings 
        "DAC_MAX":  0x10                # 8 Maximal DAC value during autoregulation (in steps of 100) while ADC is not saturated yet (not 
    }

    capabilities_by_subaddress = {val: key for key, val in capabilities.items()}

    priority_capabilities = []

    volatile = [
        "STATUS",
        "SET_AMPLITUDE",
        "AVERAGE_ADC"
    ]

#    def __init__(self, det_cfg:config.Config):
    def __init__(self, det_cfg):
        self.state = {}
        for cap in HVsysLED.capabilities:
            self.state[cap] = None


    # TODO maybe fix smth
    def valueToString(self, cap:str, value:int) -> str:
        return str(value)

    def valueFromString(self, cap:str, string:str) -> int:
        return int(string)
        
# print(HVsysLED.capabilities)

