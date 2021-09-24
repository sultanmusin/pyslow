#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from __future__ import annotations   # For neat recursive type hints

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"

import logging
import sys

class HVsysSupply800c:

    CELL_ID = 0x800c

    DESCRIPTION = "HV Supply (na61ps10c)"

    MAX_CHANNEL_COUNT = 10

    PEDESTAL_VOLTAGE_BIAS = 0         # volts. Set real ped V this much HIGHER so the per-channel voltage settings can tune both ways up and down. Set to zero for 800c boards.
    PEDESTAL_RESOLUTION = 4096        # counts
    VOLTAGE_RESOLUTION = 4096         # counts
    VOLTAGE_DECIMAL_PLACES = 2        # to 0.01 V

    POWER_OFF = 0
    POWER_ON = 1

    capabilities = {
        "CELL_ID": 0x1c,         
        "STATUS": 0x00,               # status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
        "1/SET_VOLTAGE": 0x02,
        "2/SET_VOLTAGE": 0x04,
        "3/SET_VOLTAGE": 0x06,
        "4/SET_VOLTAGE": 0x08,
        "5/SET_VOLTAGE": 0x0a,
        "6/SET_VOLTAGE": 0x0c,
        "7/SET_VOLTAGE": 0x0e,
        "8/SET_VOLTAGE": 0x10,
        "9/SET_VOLTAGE": 0x12,
        "10/SET_VOLTAGE": 0x14,
        "SET_PEDESTAL_VOLTAGE": 0x16,
        "RAMP_TIME": 0x18,
        "TEMPERATURE": 0x1a,
        "RAMP_STATUS": 0x20,
        "1/MEAS_VOLTAGE": 0x22,
        "2/MEAS_VOLTAGE": 0x24,
        "3/MEAS_VOLTAGE": 0x26,
        "4/MEAS_VOLTAGE": 0x28,
        "5/MEAS_VOLTAGE": 0x2a,
        "6/MEAS_VOLTAGE": 0x2c,
        "7/MEAS_VOLTAGE": 0x2e,
        "8/MEAS_VOLTAGE": 0x30,
        "9/MEAS_VOLTAGE": 0x32,
        "10/MEAS_VOLTAGE": 0x34,        
        "MEAS_PEDESTAL_VOLTAGE": 0x36,
        "VOLTAGE_CALIBRATION": 0x38,           # Calibration value of channels Voltage in 10mV units, i.e. to get Volts one need Vmax/100.
        "PEDESTAL_VOLTAGE_CALIBRATION": 0x3a,  # Calibration value of pedestal Voltage in 10mV units, i.e. to get Volts one need eePedVmax/100.
#        "PEDESTAL_VOLTAGE_CALIBRATION_MIN":  not available, single ped calibration for this electronics version, see above
#        "PEDESTAL_VOLTAGE_CALIBRATION_MAX":  not available, single ped calibration for this electronics version, see above
        "VERSION_DATE_LOW": 0x3c,              # Response = 8212 (0x2014)
        "VERSION_DATE_HIGH": 0x3e,             # Response = 5121 (0x1401)
        "CELL_ADDRESS": 0x41
    }

    capabilities_by_subaddress = {val: key for key, val in capabilities.items()}

    # poll these first so the voltages can be translated to string using the calibrations
    priority_capabilities = [
        "TEMPERATURE",
        "PEDESTAL_VOLTAGE_CALIBRATION", 
        "SET_PEDESTAL_VOLTAGE",
        "MEAS_PEDESTAL_VOLTAGE",
        "VOLTAGE_CALIBRATION"
    ]


    volatile = [
        "STATUS",
        "TEMPERATURE",
        "RAMP_STATUS",
        "MEAS_PEDESTAL_VOLTAGE",
        "1/MEAS_VOLTAGE",
        "2/MEAS_VOLTAGE",
        "3/MEAS_VOLTAGE",
        "4/MEAS_VOLTAGE",
        "5/MEAS_VOLTAGE",
        "6/MEAS_VOLTAGE",
        "7/MEAS_VOLTAGE",
        "8/MEAS_VOLTAGE",
        "9/MEAS_VOLTAGE",
        "10/MEAS_VOLTAGE"
    ]


#    def __init__(self, det_cfg:config.Config):
    def __init__(self, det_cfg):
        self.det_cfg = det_cfg
        self.state = {}
        for cap in HVsysSupply800c.capabilities:
            self.state[cap] = None

    def updateState(self, cap, value):
        self.state[cap] = value # TODO checks 

    def pedestalVoltsToCounts(self, volts: str) -> int:                       # also can accept float value
        volts_to_set = float(volts) + HVsysSupply800c.PEDESTAL_VOLTAGE_BIAS       # Set real ped V this much HIGHER so the per-channel voltage settings can tune both ways up and down
                                                                              # May be DANGEROUS to set ped V before per-channel V with HV ON
        calib_ped = self.state["PEDESTAL_VOLTAGE_CALIBRATION"] / 100.0     # 6248 -> 62.48 V

        # we can set values more than higher calibration so I comment out this check.
        # this_is_ok.jpg

        if volts_to_set > calib_ped:
            print("HVsysSupply800c: trying to set invalid voltage, %2.2f > %2.2f (upper bound), setting upper bound"%(volts_to_set, calib_ped))
            volts_to_set = calib_ped

        return int((HVsysSupply800c.PEDESTAL_RESOLUTION - 1) * volts_to_set / calib_ped)


    def pedestalCountsToVolts(self, counts: int) -> float:
        if counts < 0: # or counts >= HVsysSupply800c.PEDESTAL_RESOLUTION:
            raise ValueError("HVsysSupply800c: invalid pedestal counts %d >= PEDESTAL_RESOLUTION"%(counts))

        calib_ped = self.state["PEDESTAL_VOLTAGE_CALIBRATION"] / 100.0     # 5270 -> 52.70 V

        volts = counts * calib_ped / (HVsysSupply800c.PEDESTAL_RESOLUTION - 1) - HVsysSupply800c.PEDESTAL_VOLTAGE_BIAS
        return round(volts, HVsysSupply800c.VOLTAGE_DECIMAL_PLACES)

    def voltsToCounts(self, volts: str) -> int:
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysSupply800c: cannot translate volts to counts without knowing VOLTAGE_CALIBRATION")
        if "SET_PEDESTAL_VOLTAGE" not in self.state or self.state["SET_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysSupply800c: cannot translate volts to counts without knowing SET_PEDESTAL_VOLTAGE")
        pedestal_voltage = self.pedestalCountsToVolts(self.state["SET_PEDESTAL_VOLTAGE"])
        # tmp = float( self.valueToString('TEMPERATURE', self.state['TEMPERATURE']) )
        # tmp_corr = -(tmp - self.det_cfg.reference_temperature) * self.det_cfg.temperature_slope / 1000 # minus for normal temperature correction, e.g. config value 60 means "-60mV/C"
        volts_to_set = (float(volts) - pedestal_voltage - HVsysSupply800c.PEDESTAL_VOLTAGE_BIAS) # - tmp_corr  # e.g. -0.5V means we need to go 0.5V lower than pedestal (with positive counts)       

        # logging.debug("voltsToCounts: temperature correction for T=%s is %d V" % (tmp, tmp_corr))
        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 

        if volts_to_set < 0:
            print("HVsysSupply800c: trying to set invalid voltage, %2.2f < %2.2f (lower bound), setting lower bound"%(volts_to_set, 0))
            volts_to_set = 0

        if volts_to_set > calib_voltage_slope:
            print("HVsysSupply800c: trying to set invalid voltage, %2.2f > %2.2f (upper bound), setting upper bound"%(volts_to_set, calib_voltage_slope))
            volts_to_set = calib_voltage_slope

        return int((HVsysSupply800c.VOLTAGE_RESOLUTION - 1) * volts_to_set / calib_voltage_slope)

    def measVoltsToCounts(self, volts: str) -> int:
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysSupply800c: cannot translate volts to counts without knowing VOLTAGE_CALIBRATION")
        if "MEAS_PEDESTAL_VOLTAGE" not in self.state or self.state["MEAS_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysSupply800c: cannot translate volts to counts without knowing MEAS_PEDESTAL_VOLTAGE")
        pedestal_voltage = self.pedestalCountsToVolts(self.state["MEAS_PEDESTAL_VOLTAGE"])
        volts_to_set = (float(volts) - pedestal_voltage - HVsysSupply800c.PEDESTAL_VOLTAGE_BIAS)  # e.g. -0.5V means we need to go 0.5V lower than pedestal (with positive counts)       
        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 

        if volts_to_set < 0:
            print("HVsysSupply800c: trying to set invalid voltage, %2.2f < %2.2f (lower bound), setting lower bound"%(volts_to_set, 0))
            volts_to_set = 0

        if volts_to_set > calib_voltage_slope:
            print("HVsysSupply800c: trying to set invalid voltage, %2.2f > %2.2f (upper bound), setting upper bound"%(volts_to_set, calib_voltage_slope))
            volts_to_set = calib_voltage_slope

        return int((HVsysSupply800c.VOLTAGE_RESOLUTION - 1) * volts_to_set / calib_voltage_slope)

    def countsToVolts(self, counts: int) -> str:
        if counts < 0 or counts >= HVsysSupply800c.VOLTAGE_RESOLUTION:
            raise ValueError("HVsysSupply800c: invalid voltage counts %d >= VOLTAGE_RESOLUTION"%(counts))
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysSupply800c: cannot translate counts to volts without knowing VOLTAGE_CALIBRATION")
        if "SET_PEDESTAL_VOLTAGE" not in self.state or self.state["SET_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysSupply800c: cannot translate counts to volts without knowing SET_PEDESTAL_VOLTAGE")

        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 
        pedestal_voltage = self.pedestalCountsToVolts(self.state["SET_PEDESTAL_VOLTAGE"])

        # tmp = float( self.valueToString('TEMPERATURE', self.state['TEMPERATURE']) )
        # tmp_corr = -(tmp - self.det_cfg.reference_temperature) * self.det_cfg.temperature_slope / 1000 # minus for normal termerature correction, e.g. config value 60 means "-60mV/C"

        volts = pedestal_voltage + counts * calib_voltage_slope / (HVsysSupply800c.VOLTAGE_RESOLUTION - 1) + HVsysSupply800c.PEDESTAL_VOLTAGE_BIAS # - tmp_corr
        return round(volts, HVsysSupply800c.VOLTAGE_DECIMAL_PLACES)

    def measCountsToVolts(self, counts: int) -> str:
        if counts < 0 or counts >= HVsysSupply800c.VOLTAGE_RESOLUTION:
            raise ValueError("HVsysSupply800c: invalid voltage counts %d >= VOLTAGE_RESOLUTION"%(counts))
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysSupply800c: cannot translate counts to volts without knowing VOLTAGE_CALIBRATION")
        if "SET_PEDESTAL_VOLTAGE" not in self.state or self.state["MEAS_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysSupply800c: cannot translate counts to volts without knowing MEAS_PEDESTAL_VOLTAGE")

        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 
        pedestal_voltage = self.pedestalCountsToVolts(self.state["MEAS_PEDESTAL_VOLTAGE"])

        volts = pedestal_voltage + counts * calib_voltage_slope / (HVsysSupply800c.VOLTAGE_RESOLUTION - 1) + HVsysSupply800c.PEDESTAL_VOLTAGE_BIAS
        return round(volts, HVsysSupply800c.VOLTAGE_DECIMAL_PLACES)

    def tempCountsToDegrees(self, counts: int) -> float:
        return round(63.9-0.019*counts, HVsysSupply800c.VOLTAGE_DECIMAL_PLACES)


    def voltageCorrection(self): 
        if "TEMPERATURE" not in self.state or self.state["TEMPERATURE"] is None: 
            raise ValueError("HVsysSupply800c: cannot calculate temperature correction without knowing TEMPERATURE")
        tmp = self.tempCountsToDegrees(self.state['TEMPERATURE'])
        tmp_corr = (tmp - self.det_cfg.reference_temperature) * self.det_cfg.temperature_slope / 1000 # minus for normal termerature correction, e.g. config value 60 means "-60mV/C"
        
        return round(tmp_corr, HVsysSupply800c.VOLTAGE_DECIMAL_PLACES)

    convertorsFromString = {
        "1/SET_VOLTAGE": voltsToCounts,
        "2/SET_VOLTAGE": voltsToCounts,
        "3/SET_VOLTAGE": voltsToCounts,
        "4/SET_VOLTAGE": voltsToCounts,
        "5/SET_VOLTAGE": voltsToCounts,
        "6/SET_VOLTAGE": voltsToCounts,
        "7/SET_VOLTAGE": voltsToCounts,
        "8/SET_VOLTAGE": voltsToCounts,
        "9/SET_VOLTAGE": voltsToCounts,
        "10/SET_VOLTAGE": voltsToCounts,
        "SET_PEDESTAL_VOLTAGE": pedestalVoltsToCounts,
        "TEMPERATURE": lambda self, val: int(float(val*100)),
        "1/MEAS_VOLTAGE": measVoltsToCounts,
        "2/MEAS_VOLTAGE": measVoltsToCounts,
        "3/MEAS_VOLTAGE": measVoltsToCounts,
        "4/MEAS_VOLTAGE": measVoltsToCounts,
        "5/MEAS_VOLTAGE": measVoltsToCounts,
        "6/MEAS_VOLTAGE": measVoltsToCounts,
        "7/MEAS_VOLTAGE": measVoltsToCounts,
        "8/MEAS_VOLTAGE": measVoltsToCounts,
        "9/MEAS_VOLTAGE": measVoltsToCounts,
        "10/MEAS_VOLTAGE": measVoltsToCounts, 
        "MEAS_PEDESTAL_VOLTAGE": pedestalVoltsToCounts,
    }

    convertorsToString = {
        "1/SET_VOLTAGE": countsToVolts,
        "2/SET_VOLTAGE": countsToVolts,
        "3/SET_VOLTAGE": countsToVolts,
        "4/SET_VOLTAGE": countsToVolts,
        "5/SET_VOLTAGE": countsToVolts,
        "6/SET_VOLTAGE": countsToVolts,
        "7/SET_VOLTAGE": countsToVolts,
        "8/SET_VOLTAGE": countsToVolts,
        "9/SET_VOLTAGE": countsToVolts,
        "10/SET_VOLTAGE": countsToVolts,
        "SET_PEDESTAL_VOLTAGE": pedestalCountsToVolts,
        "TEMPERATURE": tempCountsToDegrees,
        "1/MEAS_VOLTAGE": measCountsToVolts,
        "2/MEAS_VOLTAGE": measCountsToVolts,
        "3/MEAS_VOLTAGE": measCountsToVolts,
        "4/MEAS_VOLTAGE": measCountsToVolts,
        "5/MEAS_VOLTAGE": measCountsToVolts,
        "6/MEAS_VOLTAGE": measCountsToVolts,
        "7/MEAS_VOLTAGE": measCountsToVolts,
        "8/MEAS_VOLTAGE": measCountsToVolts,
        "9/MEAS_VOLTAGE": measCountsToVolts,
        "10/MEAS_VOLTAGE": measCountsToVolts, 
        "MEAS_PEDESTAL_VOLTAGE": pedestalCountsToVolts,
    }

    def valueToString(self, cap:str, value:int) -> str:
        if cap in HVsysSupply800c.convertorsToString:
            method = self.convertorsToString[cap]
            result = method(self, value)
            return str(result)
        else:
            return str(value)

    def valueFromString(self, cap:str, string:str) -> int:
        if cap in HVsysSupply800c.convertorsToString:
            result = self.convertorsFromString[cap](self, string)
            return result
        else:
            return int(string)


    def has_reference_voltage(self):
        return True

""" Doc
	
	// Sub-addresses (register offsets) in na61ps10c memory
	public static byte ADDR_STATUS = 0x00;               // status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
	public static byte AddrSetVoltage(int chan) throws Exception {
		if((chan < 0) || (chan > 9)) throw new Exception("Cannot find address to set voltage for channel " + chan);
		return (byte) (0x02 + chan*2);
	}
	public static byte ADDR_SET_PEDESTAL_VOLTAGE = 0x16;
	public static byte ADDR_RAMP_TIME = 0x18;
	public static byte ADDR_TEMPERATURE = 0x1a;
	public static byte ADDR_CELL_ID = 0x1c;              
	public static byte ADDR_DUMMY = 0x1e;
	public static byte ADDR_RAMP_STATUS = 0x20; // for reading Ramp Up/Down STATus register - bits 0-9 RUD active on corresponding channel. 												Bit 10 RUD active on PedV.
	public static byte AddrMeasVoltage(int chan) throws Exception { 
		if((chan < 0) || (chan > 9)) throw new Exception("Cannot find address to set voltage for channel " + chan);
		return (byte) (0x22 + chan*2); 
	}
	public static byte ADDR_MEAS_PEDESTAL_VOLTAGE = 0x36;
	public static byte ADDR_VOLTAGE_CALIBRATION = 0x38; //(rw) Calibration value of channels Voltage in 10mV units, i.e. to get Volts one need Vmax/100.
	public static byte ADDR_PEDESTAL_VOLTAGE_CALIBRATION = 0x3a; //(rw) Calibration value of pedestal Voltage in 10mV units, i.e. to get Volts one need eePedVmax/100.
	public static byte ADDR_VERSION_DATE_LOW = 0x3c;
	public static byte ADDR_VERSION_DATE_HIGH = 0x3e;
	public static byte ADDR_NEW_CELL_ADDRESS = 0x41;
	public static int swapChannels(int id) { return 9 - ((id+9) % 10); }
"""


#s = HVsysSupply800c() 
#s.
