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
sys.path.append('.')
sys.path.append('lib/hvsys')
from message import Message

class HVsysSupply:

    CELL_ID = 0x8013 

    DESCRIPTION = "HV Supply"

    MAX_CHANNEL_COUNT = 10

    PEDESTAL_VOLTAGE_BIAS = 1.6       # volts. Set real ped V this much HIGHER so the per-channel voltage settings can tune both ways up and down
    PEDESTAL_RESOLUTION = 4096        # counts
    VOLTAGE_RESOLUTION = 4096         # counts
    VOLTAGE_DECIMAL_PLACES = 2        # to 0.01 V

    POWER_OFF = 0
    POWER_ON = 1

    capabilities = {
        "CELL_ID": 0x00,         
        "STATUS": 0x02,               # status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
                                      # "SET_VOLTAGE": list(range(0x04, 0x04 + 2 * CHANNEL_COUNT, 2)),
        "1/SET_VOLTAGE": 0x04,
        "2/SET_VOLTAGE": 0x06,
        "3/SET_VOLTAGE": 0x08,
        "4/SET_VOLTAGE": 0x0a,
        "5/SET_VOLTAGE": 0x0c,
        "6/SET_VOLTAGE": 0x0e,
        "7/SET_VOLTAGE": 0x10,
        "8/SET_VOLTAGE": 0x12,
        "9/SET_VOLTAGE": 0x14,
        "10/SET_VOLTAGE": 0x16,
        "SET_PEDESTAL_VOLTAGE": 0x18,
        "RAMP_TIME": 0x26,
        "TEMPERATURE": 0x28,
        "RAMP_STATUS": 0x2c,
        "1/MEAS_VOLTAGE": 0x2e,
        "2/MEAS_VOLTAGE": 0x30,
        "3/MEAS_VOLTAGE": 0x32,
        "4/MEAS_VOLTAGE": 0x34,
        "5/MEAS_VOLTAGE": 0x36,
        "6/MEAS_VOLTAGE": 0x38,
        "7/MEAS_VOLTAGE": 0x3a,
        "8/MEAS_VOLTAGE": 0x3c,
        "9/MEAS_VOLTAGE": 0x3e,
        "10/MEAS_VOLTAGE": 0x40,        
        #"MEAS_VOLTAGE": list(range(0x2e, 0x2e + 2 * CHANNEL_COUNT, 2)),
        "MEAS_PEDESTAL_VOLTAGE": 0x42,
        "VOLTAGE_CALIBRATION": 0x50,
        "PEDESTAL_VOLTAGE_CALIBRATION_MIN": 0x54,  # TODO check typo
        "PEDESTAL_VOLTAGE_CALIBRATION_MAX": 0x52,
        "VERSION_DATE_LOW": 0x56,
        "VERSION_DATE_HIGH": 0x58,
        "CELL_ADDRESS": 0x5c
    }

    capabilities_by_subaddress = {val: key for key, val in capabilities.items()}

    # poll these first so the voltages can be translated to string using the calibrations
    priority_capabilities = [
        "VOLTAGE_CALIBRATION",
        "PEDESTAL_VOLTAGE_CALIBRATION_MIN", 
        "PEDESTAL_VOLTAGE_CALIBRATION_MAX",
        "SET_PEDESTAL_VOLTAGE",
        "MEAS_PEDESTAL_VOLTAGE",
        "TEMPERATURE",
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


    def __init__(self, config):
        self.config = config
        self.state = {}
        for cap in HVsysSupply.capabilities:
            self.state[cap] = None

        self.state['REF_PEDESTAL_VOLTAGE'] = self.config.hv_pedestal
        for ch in range(1,self.config.n_channels+1):
            self.state[f"{ch}/REF_VOLTAGE"] = self.config.hv[str(ch)]
        
        if hasattr(config, 'temperature_sensor'):
            self.temperature_sensor = config.temperature_sensor
        else:
            self.temperature_sensor = self

    # set another module (can be any object with state['TEMPERATURE'] property) as the source for this module temp correction
    def set_temperature_sensor(self, temperature_sensor):
        self.temperature_sensor = temperature_sensor


    def reference_voltage_caps(self):
        return [f"{ch}/REF_VOLTAGE" for ch in range(1, self.config.n_channels+1)] + ['REF_PEDESTAL_VOLTAGE']


    def updateState(self, cap, value):
        self.state[cap] = value # TODO checks 

    def pedestalVoltsToCounts(self, volts: str) -> int:                       # also can accept float value
        volts_to_set = float(volts) + HVsysSupply.PEDESTAL_VOLTAGE_BIAS       # Set real ped V this much HIGHER so the per-channel voltage settings can tune both ways up and down
                                                                              # May be DANGEROUS to set ped V before per-channel V with HV ON
        calib_ped_high = self.state["PEDESTAL_VOLTAGE_CALIBRATION_MAX"] / 100.0     # 6248 -> 62.48 V
        calib_ped_low = self.state["PEDESTAL_VOLTAGE_CALIBRATION_MIN"] / 100.0      # 4953 -> 49.53 V

        if volts_to_set < calib_ped_low:
            print("HVsysSupply: trying to set invalid voltage, %2.2f < %2.2f (lower bound), setting lower bound"%(volts_to_set, calib_ped_low))
            volts_to_set = calib_ped_low

        # we can set values more than higher calibration so I comment out this check.
        # this_is_ok.jpg

        #if volts_to_set > calib_ped_high:
        #    print("HVsysSupply: trying to set invalid voltage, %2.2f > %2.2f (upper bound), setting upper bound"%(volts_to_set, calib_ped_high))
        #    volts_to_set = calib_ped_high

        return int((HVsysSupply.PEDESTAL_RESOLUTION - 1) * (volts_to_set - calib_ped_low) / (calib_ped_high - calib_ped_low))


    def pedestalCountsToVolts(self, counts: int) -> float:
        if counts < 0: # or counts >= HVsysSupply.PEDESTAL_RESOLUTION:
            raise ValueError("HVsysSupply: invalid pedestal counts %d >= PEDESTAL_RESOLUTION"%(counts))

        calib_ped_high = self.state["PEDESTAL_VOLTAGE_CALIBRATION_MAX"] / 100.0     # 5270 -> 52.70 V
        calib_ped_low = self.state["PEDESTAL_VOLTAGE_CALIBRATION_MIN"] / 100.0      # 3180 -> 31.80 V

        volts = calib_ped_low + counts * (calib_ped_high - calib_ped_low) / (HVsysSupply.PEDESTAL_RESOLUTION - 1) - HVsysSupply.PEDESTAL_VOLTAGE_BIAS
        return round(volts, HVsysSupply.VOLTAGE_DECIMAL_PLACES)

    def voltsToCounts(self, volts: str) -> int:
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysSupply: cannot translate volts to counts without knowing VOLTAGE_CALIBRATION")
        if "REF_PEDESTAL_VOLTAGE" not in self.state or self.state["REF_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysSupply: cannot translate volts to counts without knowing REF_PEDESTAL_VOLTAGE")
        pedestal_voltage = float(self.state["REF_PEDESTAL_VOLTAGE"])
        volts_to_set = pedestal_voltage + HVsysSupply.PEDESTAL_VOLTAGE_BIAS - float(volts)  # e.g. -0.5V means we need to go 0.5V lower than pedestal (with positive counts)       

        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 

        if volts_to_set < 0:
            logging.warning(f"HVsysSupply id={self.config.id}: trying to set invalid voltage, {volts_to_set} < 0 (lower bound), setting lower bound")
            volts_to_set = 0

        if volts_to_set > calib_voltage_slope:
            print(f"HVsysSupply id={self.config.id}: trying to set invalid voltage, {volts_to_set} > {calib_voltage_slope} (upper bound), setting upper bound")
            volts_to_set = calib_voltage_slope

        return int((HVsysSupply.VOLTAGE_RESOLUTION - 1) * volts_to_set / calib_voltage_slope)

    def measVoltsToCounts(self, volts: str) -> int:
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysSupply: cannot translate volts to counts without knowing VOLTAGE_CALIBRATION")
        if "MEAS_PEDESTAL_VOLTAGE" not in self.state or self.state["MEAS_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysSupply: cannot translate volts to counts without knowing MEAS_PEDESTAL_VOLTAGE")
        pedestal_voltage = self.pedestalCountsToVolts(self.state["MEAS_PEDESTAL_VOLTAGE"])
        volts_to_set = -(float(volts) - pedestal_voltage - HVsysSupply.PEDESTAL_VOLTAGE_BIAS)  # e.g. -0.5V means we need to go 0.5V lower than pedestal (with positive counts)       
        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 

        if volts_to_set < 0:
            print("HVsysSupply: trying to set invalid voltage, %2.2f < %2.2f (lower bound), setting lower bound"%(volts_to_set, 0))
            volts_to_set = 0

        if volts_to_set > calib_voltage_slope:
            print("HVsysSupply: trying to set invalid voltage, %2.2f > %2.2f (upper bound), setting upper bound"%(volts_to_set, calib_voltage_slope))
            volts_to_set = calib_voltage_slope

        return int((HVsysSupply.VOLTAGE_RESOLUTION - 1) * volts_to_set / calib_voltage_slope)

    def countsToVolts(self, counts: int) -> str:
        if counts < 0 or counts >= HVsysSupply.VOLTAGE_RESOLUTION:
            raise ValueError("HVsysSupply: invalid voltage counts %d >= VOLTAGE_RESOLUTION"%(counts))
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysSupply: cannot translate counts to volts without knowing VOLTAGE_CALIBRATION")
        if "SET_PEDESTAL_VOLTAGE" not in self.state or self.state["SET_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysSupply: cannot translate counts to volts without knowing SET_PEDESTAL_VOLTAGE")

        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 
        pedestal_voltage = self.pedestalCountsToVolts(self.state["SET_PEDESTAL_VOLTAGE"])

        tmp = float( self.valueToString('TEMPERATURE', self.temperature_sensor.state['TEMPERATURE']) )
        tmp_corr = -(tmp - self.config.reference_temperature) * self.config.temperature_slope / 1000 # minus for normal termerature correction, e.g. config value 60 means "-60mV/C"

        volts = pedestal_voltage - counts * calib_voltage_slope / (HVsysSupply.VOLTAGE_RESOLUTION - 1) + HVsysSupply.PEDESTAL_VOLTAGE_BIAS + tmp_corr
        return round(volts, HVsysSupply.VOLTAGE_DECIMAL_PLACES)

    def measCountsToVolts(self, counts: int) -> str:
        if counts < 0 or counts >= HVsysSupply.VOLTAGE_RESOLUTION:
            raise ValueError("HVsysSupply: invalid voltage counts %d >= VOLTAGE_RESOLUTION"%(counts))
        if "VOLTAGE_CALIBRATION" not in self.state or self.state["VOLTAGE_CALIBRATION"] is None: 
            raise ValueError("HVsysSupply: cannot translate counts to volts without knowing VOLTAGE_CALIBRATION")
        if "SET_PEDESTAL_VOLTAGE" not in self.state or self.state["MEAS_PEDESTAL_VOLTAGE"] is None: 
            raise ValueError("HVsysSupply: cannot translate counts to volts without knowing MEAS_PEDESTAL_VOLTAGE")

        calib_voltage_slope = self.state["VOLTAGE_CALIBRATION"] / 100.0              #  325 -> -3.25 V (full scale) 
        pedestal_voltage = self.pedestalCountsToVolts(self.state["MEAS_PEDESTAL_VOLTAGE"])

        volts = pedestal_voltage - counts * calib_voltage_slope / (HVsysSupply.VOLTAGE_RESOLUTION - 1) + HVsysSupply.PEDESTAL_VOLTAGE_BIAS
        return round(volts, HVsysSupply.VOLTAGE_DECIMAL_PLACES)

    def tempCountsToDegrees(self, counts: int) -> float:
        if self.config.temperature_from_module == 'FAKE':
            return self.config.reference_temperature - 1
        else:
            return round(63.9-0.019*counts, HVsysSupply.VOLTAGE_DECIMAL_PLACES)

    def tempDegreesToCounts(self, degrees: float) -> int:
        # we'll probably never need setting the temperature...
        return int((63.9-degrees)/0.019)


    def voltage_correction(self): 
        if "TEMPERATURE" not in self.temperature_sensor.state or self.temperature_sensor.state["TEMPERATURE"] is None: 
            raise ValueError(f"HVsysSupply id={self.config.id} addr={self.config.address('hv')}: cannot calculate correction without knowing TEMPERATURE (sensor id={self.temperature_sensor.config.id} addr={self.temperature_sensor.config.address('hv')})")
        tmp = self.tempCountsToDegrees(self.temperature_sensor.state['TEMPERATURE'])
        tmp_corr = (tmp - self.config.reference_temperature) * self.config.temperature_slope / 1000 # minus for normal termerature correction, e.g. config value 60 means "-60mV/C"

        #logging.debug(round(tmp_corr, HVsysSupply.VOLTAGE_DECIMAL_PLACES))
        return round(tmp_corr, HVsysSupply.VOLTAGE_DECIMAL_PLACES)

    convertorsFromString = {
        "TEMPERATURE": tempDegreesToCounts,
        "1/REF_VOLTAGE": voltsToCounts,
        "2/REF_VOLTAGE": voltsToCounts,
        "3/REF_VOLTAGE": voltsToCounts,
        "4/REF_VOLTAGE": voltsToCounts,
        "5/REF_VOLTAGE": voltsToCounts,
        "6/REF_VOLTAGE": voltsToCounts,
        "7/REF_VOLTAGE": voltsToCounts,
        "8/REF_VOLTAGE": voltsToCounts,
        "9/REF_VOLTAGE": voltsToCounts,
        "10/REF_VOLTAGE": voltsToCounts,
        "REF_PEDESTAL_VOLTAGE": pedestalVoltsToCounts,
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
        "TEMPERATURE": tempCountsToDegrees,
        "1/REF_VOLTAGE": countsToVolts,
        "2/REF_VOLTAGE": countsToVolts,
        "3/REF_VOLTAGE": countsToVolts,
        "4/REF_VOLTAGE": countsToVolts,
        "5/REF_VOLTAGE": countsToVolts,
        "6/REF_VOLTAGE": countsToVolts,
        "7/REF_VOLTAGE": countsToVolts,
        "8/REF_VOLTAGE": countsToVolts,
        "9/REF_VOLTAGE": countsToVolts,
        "10/REF_VOLTAGE": countsToVolts,
        "REF_PEDESTAL_VOLTAGE": pedestalCountsToVolts,
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
        if cap in HVsysSupply.convertorsToString:
            method = self.convertorsToString[cap]
            result = method(self, value)
            return str(result)
        else:
            return str(value)

    def valueFromString(self, cap:str, string:str) -> int:
        if cap in HVsysSupply.convertorsToString:
            result = self.convertorsFromString[cap](self, string)
            return result
        else:
            return int(string)


    def has_reference_voltage(self):
        return True


    def request_voltage_change(self, cap, new_voltage) -> Message:
        # cap should be one of N/REF_VOLTAGE or REF_PEDESTAL_VOLTAGE
        if cap not in self.reference_voltage_caps(): 
            return None

        old_voltage = float(self.state[cap])
        self.state[cap] = new_voltage
        corrected_voltage = float(new_voltage) + self.voltage_correction()

        logging.info(f"Request {cap} change (id={self.config.id}) old={old_voltage} new={new_voltage} corrected={corrected_voltage}")

        if cap == 'REF_PEDESTAL_VOLTAGE':     # also update all the channel voltages
            for ch in range(1, self.config.n_channels+1):
                self.state[f'{ch}/REF_VOLTAGE'] += (float(new_voltage) - old_voltage)
        
        set_cap = cap.replace('REF', 'SET')     # 4/REF_VOLTAGE -> 4/SET_VOLTAGE to construct the command
        set_value = self.valueFromString(set_cap, corrected_voltage if cap == 'REF_PEDESTAL_VOLTAGE' else new_voltage) # apply correction ONLY to pedestal
        command = Message(Message.WRITE_SHORT, self.config.addr['hv'], self, set_cap, set_value)
        return command


    def request_voltage_correction(self) -> Message:
        set_value = self.valueFromString('SET_PEDESTAL_VOLTAGE', self.state['REQ_PEDESTAL_VOLTAGE'])
        command = Message(Message.WRITE_SHORT, self.config.addr['hv'], self, 'SET_PEDESTAL_VOLTAGE', set_value)
        return command

""" Doc
	
	public int PED_CALIB_MIN = 0;
	public int PED_CALIB_MAX = 0;
	public int CHAN_CALIB = 0;

	// Sub-addresses (register offsets) in na61ps10c memory
	public static byte ADDR_STATUS = 0x02;               // status -  error i.e. in process of settings - stat=avADC-ADCsetpt;
	public static byte AddrSetVoltage(int chan) throws Exception {
		if((chan < 0) || (chan > 9)) throw new Exception("Cannot find address to set voltage for channel " + chan);
		return (byte) (0x04 + chan*2);
	}
	public static byte ADDR_SET_PEDESTAL_VOLTAGE = 0x18;
	public static byte ADDR_RAMP_TIME = 0x26;
	public static byte ADDR_TEMPERATURE = 0x28;
	public static byte ADDR_CELL_ID = 0x00;              
	public static byte ADDR_DUMMY = 0x1e;
	public static byte ADDR_RAMP_STATUS = 0x2c;
	public static byte AddrMeasVoltage(int chan) throws Exception { 
		if((chan < 0) || (chan > 9)) throw new Exception("Cannot find address to set voltage for channel " + chan);
		return (byte) (0x2e + chan*2); 
	}
	public static byte ADDR_MEAS_PEDESTAL_VOLTAGE = 0x42;
	public static byte ADDR_VOLTAGE_CALIBRATION = 0x50;
	public static byte ADDR_PEDESTAL_VOLTAGE_CALIBRATION_MIN = 0x54;
	public static byte ADDR_PEDESTAL_VOLTAGE_CALIBRATION_MAX = 0x52;
	public static byte ADDR_VERSION_DATE_LOW = 0x56;
	public static byte ADDR_VERSION_DATE_HIGH = 0x58;
	public static byte ADDR_NEW_CELL_ADDRESS = 0x5c;
"""
